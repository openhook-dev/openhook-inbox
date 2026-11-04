"""Binary transfers stay outside MCP/model context; every download reauthorizes."""
import re
from urllib.parse import quote, unquote_to_bytes

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.responses import JSONResponse, Response

from openhook.channel_files import ChannelFiles, FILE_DEFAULT_EXPIRY, validate_filename, validate_upload
from openhook.errors import ChannelError
from openhook.http_errors import problem
from openhook.session_api import parse_call


class FileAccess(BaseModel):
    model_config = ConfigDict(extra='forbid')
    participant_token: str = Field(min_length=1, max_length=100)


async def upload_file(request):
    try:
        if request.url.query:
            raise ChannelError('File transfers do not accept query parameters.')
        if request.headers.get('content-type', '').lower() != 'application/octet-stream':
            raise ChannelError('Upload raw bytes with Content-Type: application/octet-stream.', 415)
        if request.headers.get('content-encoding', 'identity').lower() != 'identity':
            raise ChannelError('Compressed HTTP request bodies are not supported.', 415)
        authorization = request.headers.get('authorization', '')
        token = authorization[7:] if authorization.startswith('Bearer ') else ''
        service = ChannelFiles(request.app.state.store)
        service.prepare(token)  # Reject unauthorized uploads before buffering bytes.
        name = request.headers.get('x-openhook-filename', '')
        if re.search(r'%(?![0-9a-fA-F]{2})', name):
            raise ChannelError('Percent-encode the UTF-8 filename.')
        filename = unquote_to_bytes(name).decode('utf-8')
        validate_filename(filename)
        expiry = request.headers.get('x-openhook-expiry', str(FILE_DEFAULT_EXPIRY))
        if not re.fullmatch(r'[0-9]{1,6}', expiry):
            raise ChannelError('Use an attachment expiry in seconds, at most 7 days.')
        upload_id = request.headers.get('x-openhook-upload-id', '')
        validate_upload(filename, upload_id, int(expiry))
        result = service.upload(token, filename, await request.body(), upload_id, int(expiry))
        return JSONResponse({'success': True, 'data': result}, status_code=200 if result['duplicate'] else 201)
    except ChannelError as exc:
        return problem(exc.status, str(exc))
    except (ValueError, UnicodeError):
        return problem(400, 'Invalid attachment headers.')


async def download_file(request):
    try:
        if request.url.query:
            raise ChannelError('File transfers do not accept query parameters.')
        call = await parse_call(request, FileAccess)
    except ChannelError as exc:
        return problem(exc.status, str(exc))
    except (ValidationError, ValueError, RecursionError):
        return problem(400, 'Invalid file access fields.')
    try:
        metadata, content = ChannelFiles(request.app.state.store).download(
            call.participant_token, request.path_params['file_id'])
        return Response(content, media_type='application/octet-stream', headers={
            'Content-Disposition': "attachment; filename*=UTF-8''" + quote(metadata['filename'], safe=''),
            'Content-Security-Policy': "sandbox; default-src 'none'",
        })
    except ChannelError as exc:
        return problem(exc.status, str(exc))
