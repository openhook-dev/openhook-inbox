"""Explicit entry point for the hosted service."""

import argparse

from openhook.web import create_app as core_app
from openhook_hosted.hosted_web import ROUTES
from openhook_hosted.settings import HostedSettings


def create_app(settings: HostedSettings | None = None):
    return core_app(settings or HostedSettings.from_env(), hosted_routes=ROUTES)


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description="Openhook hosted accounts and billing")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args()
    uvicorn.run(create_app(), host=args.host, port=args.port, access_log=False)
