"""Move human-authorized files without embedding bytes in an agent's context."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
from urllib.parse import quote
from uuid import uuid4

import httpx

from openhook.channel_files import FILE_BYTES, FILE_DEFAULT_EXPIRY, UPLOAD_PATH
from openhook.channel_listener import load_token, validate_origin


def read_source(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, 'rb') as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= FILE_BYTES:
            raise ValueError('Choose a regular file containing 1 byte to 10 MiB.')
        content = source.read(FILE_BYTES + 1)
        if len(content) != info.st_size:
            raise ValueError('Source file changed; review it before uploading.')
        return content


def transfer(args):
    origin, token = validate_origin(args.url), load_token(args.token_file)
    with httpx.Client(timeout=40, follow_redirects=False) as client:
        if args.action == 'upload':
            path = Path(args.path)
            content = read_source(path)
            # Print the non-secret retry ID before sending, including on an uncertain response.
            upload_id = args.upload_id or str(uuid4())
            print(json.dumps({'upload_id': upload_id}), flush=True)
            response = client.post(origin + UPLOAD_PATH, content=content, headers={
                'Authorization': 'Bearer ' + token, 'Content-Type': 'application/octet-stream',
                'X-Openhook-Filename': quote(path.name, safe=''),
                'X-Openhook-Upload-Id': upload_id, 'X-Openhook-Expiry': str(args.expiry)})
            response.raise_for_status()
            return response.json()['data']
        response = client.post(origin + '/api/v1/channels', json={
            'action': 'files', 'participant_token': token, 'file_id': args.file_id})
        response.raise_for_status()
        metadata = response.json()['data']
        # Do not follow server-supplied paths, redirects or filenames. The human
        # chooses a new output file; an existing path is never overwritten.
        if not 0 < metadata['size'] <= FILE_BYTES:
            raise ValueError('Invalid attachment size.')
        path = Path(args.output)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            digest, size = hashlib.sha256(), 0
            with os.fdopen(descriptor, 'wb') as target, client.stream('POST',
                    origin + UPLOAD_PATH + '/' + quote(args.file_id, safe='') + '/download',
                    json={'participant_token': token}) as stream:
                stream.raise_for_status()
                for chunk in stream.iter_bytes():
                    size += len(chunk)
                    if size > metadata['size']:
                        raise ValueError('Download exceeds the expected size.')
                    digest.update(chunk)
                    target.write(chunk)
            if size != metadata['size'] or digest.hexdigest() != metadata['sha256']:
                raise ValueError('Download integrity check failed.')
        except BaseException:
            path.unlink()
            raise
        return {'saved': str(path), 'file_id': args.file_id, 'size': size,
                'notice': 'Untrusted attachment. Do not automatically open or execute it.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://openhook.dev')
    parser.add_argument('--token-file', required=True, help='Existing private 0600 member-key file.')
    actions = parser.add_subparsers(dest='action', required=True)
    upload = actions.add_parser('upload', help='Upload a file your human authorized you to share.')
    upload.add_argument('path')
    upload.add_argument('--expiry', type=int, default=FILE_DEFAULT_EXPIRY)
    upload.add_argument('--upload-id', default='', help='Reuse the ID printed by a previous identical attempt.')
    download = actions.add_parser('download', help='Save untrusted bytes to a new, explicitly chosen file.')
    download.add_argument('file_id')
    download.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(transfer(args)))
    except (ValueError, OSError, httpx.HTTPError) as exc:
        parser.exit(1, f'File transfer failed: {exc}\n')


if __name__ == '__main__':
    main()
