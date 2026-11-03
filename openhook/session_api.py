"""HTTP adapter. Secrets travel only in POST bodies, never query strings."""

from typing import Literal
import json

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.responses import JSONResponse

from openhook.errors import ChannelError
from openhook.http_errors import problem
from openhook.sessions import Sessions, CHANNEL_DEFAULT_EXPIRY, CHANNEL_MAX_EXPIRY


class ChannelCall(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: Literal['create', 'invite', 'join', 'info', 'revoke', 'send', 'read', 'close', 'rotate', 'leave', 'archive', 'renew']
    participant_token: str = Field(default='', max_length=100)
    invite_code: str = Field(default='', max_length=2048, description='Full invite URL or single-use ohi_ code.')
    participant_id: str = Field(default='', max_length=100)
    name: str = Field(default='', max_length=80)
    title: str = Field(default='', max_length=160)
    expiry: int = Field(default=CHANNEL_DEFAULT_EXPIRY, ge=60, le=CHANNEL_MAX_EXPIRY)
    permission: Literal['read', 'write'] = 'write'
    scope: str = Field(default='', max_length=2000)
    archived: bool = True
    text: str = Field(default='', max_length=16384)
    message_id: str = Field(default='', max_length=80)
    since: int = Field(default=0, ge=0, le=2**63-1)
    timeout_seconds: float = Field(default=0, ge=0, le=30, allow_inf_nan=False)


def unique_fields(pairs):
    values = {}
    for key, value in pairs:
        if key in values:
            raise ValueError('Duplicate JSON field')
        values[key] = value
    return values


def reject_constant(value):
    raise ValueError('Nonstandard JSON number')


async def session_call(request):
    if request.headers.get('content-type', '').split(';', 1)[0].strip().lower() != 'application/json':
        return problem(415, 'Use Content-Type: application/json with a UTF-8 JSON body.')
    if request.headers.get('content-encoding', 'identity').strip().lower() != 'identity':
        return problem(415, 'Compressed request bodies are not supported.')
    try:
        payload = json.loads((await request.body()).decode('utf-8'),
                             object_pairs_hook=unique_fields, parse_constant=reject_constant)
        call = ChannelCall.model_validate(payload)
        sessions = Sessions(request.app.state.store)
        token = call.participant_token
        if call.action == 'create':
            result = sessions.create(call.name, call.title, call.expiry, channel=True, scope=call.scope)
        elif call.action == 'join':
            result = sessions.join(call.invite_code, call.name)
        elif call.action == 'invite':
            result = sessions.invite(token, call.permission)
        elif call.action == 'info':
            result = sessions.info(token)
        elif call.action == 'revoke':
            result = sessions.revoke(token, call.participant_id)
        elif call.action == 'send':
            result = sessions.send(token, call.text, call.message_id)
        elif call.action == 'read':
            result = await sessions.wait(token, call.since, call.timeout_seconds)
        elif call.action == 'rotate':
            result = sessions.rotate(token)
        elif call.action == 'leave':
            result = sessions.leave(token)
        elif call.action == 'archive':
            result = sessions.archive(token, call.archived)
        elif call.action == 'renew':
            result = sessions.renew(token, call.expiry)
        else:
            result = sessions.close(token)
        return JSONResponse({'success': True, 'data': result})
    except ChannelError as exc:
        return problem(exc.status, str(exc))
    except (ValidationError, ValueError, RecursionError):
        return problem(400, 'Invalid channel fields. Check /openapi.json.')
