"""HTTP adapter. Secrets travel only in POST bodies, never query strings."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.responses import JSONResponse

from openhook.errors import InboxError
from openhook.http_errors import problem
from openhook.sessions import Sessions


class SessionCall(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: Literal['create', 'invite', 'join', 'info', 'approve', 'revoke', 'send', 'read', 'close']
    participant_token: str = Field(default='', max_length=100)
    invite_code: str = Field(default='', max_length=100)
    participant_id: str = Field(default='', max_length=100)
    name: str = Field(default='', max_length=80)
    title: str = Field(default='', max_length=160)
    expiry: int = Field(default=86400, ge=60, le=604800)
    text: str = Field(default='', max_length=16384)
    message_id: str = Field(default='', max_length=80)
    since: int = Field(default=0, ge=0, le=2**63-1)
    timeout_seconds: float = Field(default=0, ge=0, le=30, allow_inf_nan=False)


async def session_call(request):
    try:
        call = SessionCall.model_validate(await request.json())
        sessions = Sessions(request.app.state.store)
        token = call.participant_token
        if call.action == 'create':
            result = sessions.create(call.name, call.title, call.expiry)
        elif call.action == 'join':
            result = sessions.join(call.invite_code, call.name)
        elif call.action == 'invite':
            result = sessions.invite(token)
        elif call.action == 'info':
            result = sessions.info(token)
        elif call.action in {'approve', 'revoke'}:
            result = sessions.set_participant(token, call.participant_id, approve=call.action == 'approve')
        elif call.action == 'send':
            result = sessions.send(token, call.text, call.message_id)
        elif call.action == 'read':
            result = await sessions.wait(token, call.since, call.timeout_seconds)
        else:
            result = sessions.close(token)
        return JSONResponse({'success': True, 'data': result})
    except InboxError as exc:
        return problem(exc.status, str(exc))
    except (ValidationError, ValueError):
        return problem(400, 'Invalid session fields. Check /openapi.json.')
