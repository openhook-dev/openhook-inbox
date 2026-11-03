"""Generate a private storage key ring, without writing keys to stdout."""
import argparse
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet


def generate(destination):
    destination = Path(destination).expanduser()
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, 'w') as output:
        json.dump([Fernet.generate_key().decode('ascii')], output)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', help='New private key-ring file; existing files are never overwritten')
    args = parser.parse_args()
    generate(args.destination)
    print('Private storage key ring created. Back it up separately from the database; never commit or share it.')
