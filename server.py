#!/usr/bin/env python3
"""Run Openhook's native MCP server and optional capture transports."""

from __future__ import annotations

import argparse
from contextlib import asynccontextmanager

from mcp.server import MCPServer

from openhook.settings import Settings
from openhook.store import Store
from openhook.tools import register_tools


def build_mcp(settings: Settings | None = None):
    @asynccontextmanager
    async def lifespan(_server):
        yield Store(settings or Settings.from_env())

    result = MCPServer(
        "openhook", title="Openhook", version="0.1.0",
        description="Self-hosted webhook, email, and DNS inboxes for AI agents.",
        website_url="https://openhook.dev",
        instructions="Create an inbox and save its private management token. Share its capture addresses with senders. "
        "Use wait_for_request with a sequence cursor to receive events. Capture URLs do not grant read access. "
        "Openhook operates its own capture servers and durable storage.",
        lifespan=lifespan,
    )
    register_tools(result)
    return result


mcp = build_mcp()


def run_server() -> None:
    """Synchronous entry point for the console script."""
    parser = argparse.ArgumentParser(description="Openhook: webhook inboxes for AI agents")
    parser.add_argument("--http", action="store_true", help="Serve the website, web API, and MCP over HTTP")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args()
    if args.http:
        import uvicorn
        from web_app import create_app
        uvicorn.run(create_app(), host=args.host, port=args.port, access_log=False)
    else:
        mcp.run()


if __name__ == "__main__":
    run_server()
