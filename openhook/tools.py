"""MCP tools backed exclusively by Openhook's own store."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.types import ToolAnnotations

from openhook.store import InboxError, Store
from openhook.providers import register, remove

READ = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=False)
DELETE = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=False)
PROVIDER_WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=True)
PROVIDER_DELETE = ToolAnnotations(read_only_hint=False, destructive_hint=True, open_world_hint=True)
Kind = Literal["web", "email", "dns"]


def store(ctx: Context) -> Store:
    return ctx.request_context.lifespan_context


def register_tools(mcp: MCPServer) -> None:
    @mcp.tool(annotations=READ)
    def server_status(ctx: Context) -> dict:
        """Inspect native storage, retention, and enabled capture transports."""
        settings = store(ctx).settings
        return {"product": "openhook", "version": "0.1.0", "origin": settings.origin,
                "storage": "sqlite", "http": True, "email": bool(settings.email_domain),
                "dns": bool(settings.dns_domain), "retention_seconds": 604800,
                "max_events_per_inbox": settings.event_limit, "max_event_bytes": settings.body_limit}

    @mcp.tool(annotations=WRITE)
    def create_webhook(ctx: Context, expiry: int = 604800, name: str = "") -> dict:
        """Create an inbox. Save its private token; share only its public capture addresses."""
        return store(ctx).create(expiry=expiry, name=name)

    @mcp.tool(annotations=WRITE)
    def configure_webhook(ctx: Context, webhook_token: str, default_status: int | None = None,
                          default_content: str | dict | list | None = None, default_content_type: str | None = None,
                          cors: bool | None = None, verification_secret: str | None = None,
                          signature_provider: Literal["generic", "github", "stripe", "linear"] | None = None) -> dict:
        """Set HTTP responses and optional SHA256 HMAC verification, preserving unspecified fields."""
        content = json.dumps(default_content) if isinstance(default_content, (dict, list)) else default_content
        values = {"default_status": default_status, "default_content": content,
                  "default_content_type": default_content_type, "cors": cors,
                  "verification_secret": verification_secret, "signature_provider": signature_provider}
        return store(ctx).configure(webhook_token, {key: value for key, value in values.items() if value is not None})

    @mcp.tool(annotations=READ)
    def get_webhook_info(ctx: Context, webhook_token: str) -> dict:
        """Read addresses, expiry, response settings, and retained event count."""
        return store(ctx).info(webhook_token)

    @mcp.tool(annotations=READ)
    def get_webhook_email(ctx: Context, webhook_token: str) -> dict:
        """Read the email address, available when this deployment runs SMTP."""
        return {"email": store(ctx).info(webhook_token)["email"]}

    @mcp.tool(annotations=PROVIDER_WRITE)
    async def register_github_webhook(ctx: Context, access_token: str, repository: str, events: list[str]) -> dict:
        """Create a signed GitHub repository subscription and native inbox. Requires webhook-write permission."""
        return await register(store(ctx), "github", access_token, events, repository)

    @mcp.tool(annotations=PROVIDER_WRITE)
    async def register_stripe_webhook(ctx: Context, access_token: str, events: list[str]) -> dict:
        """Create a signed Stripe webhook endpoint and native inbox. Provider credentials are not stored."""
        return await register(store(ctx), "stripe", access_token, events)

    @mcp.tool(annotations=PROVIDER_WRITE)
    async def register_linear_webhook(ctx: Context, access_token: str, resource_types: list[str], team_id: str = "") -> dict:
        """Create a signed Linear subscription and native inbox. Requires admin scope; optional team filter."""
        return await register(store(ctx), "linear", access_token, resource_types, team_id)

    @mcp.tool(annotations=PROVIDER_DELETE)
    async def unregister_webhook(ctx: Context, webhook_token: str, access_token: str) -> dict:
        """Remove the registered provider subscription and permanently delete its native inbox and events."""
        subscription = store(ctx).info(webhook_token)["subscription"]
        if not subscription:
            raise InboxError("This inbox has no provider subscription.")
        store(ctx).record_activity(webhook_token, "subscription.removal_started", {"provider": subscription["provider"]})
        try:
            await remove(subscription["provider"], access_token, subscription["external_id"], subscription["target"])
        except Exception as exc:
            store(ctx).record_activity(webhook_token, "subscription.removal_failed", {"provider": subscription["provider"], "error_type": type(exc).__name__})
            raise
        store(ctx).detach_subscription(webhook_token)
        return store(ctx).delete(webhook_token)

    @mcp.tool(annotations=DELETE)
    def delete_webhook(ctx: Context, webhook_token: str) -> dict:
        """Permanently delete this inbox and its stored events."""
        return store(ctx).delete(webhook_token)

    @mcp.tool(annotations=DELETE)
    def rotate_webhook_token(ctx: Context, webhook_token: str) -> dict:
        """Revoke the old private token and return a new one; capture addresses stay unchanged."""
        return store(ctx).rotate(webhook_token)

    @mcp.tool(annotations=READ)
    def get_webhook_requests(ctx: Context, webhook_token: str, limit: int = 50,
                             page: int = 1, since: int = 0, request_type: Kind | None = None) -> dict:
        """Read events with pagination or a durable sequence cursor."""
        return store(ctx).requests(webhook_token, limit=limit, page=page, since=since, request_type=request_type)

    @mcp.tool(annotations=READ)
    def get_webhook_activity(ctx: Context, webhook_token: str, since: int = 0, limit: int = 100) -> dict:
        """Read durable receipt and mutation history with a cursor. Bodies and secrets are excluded."""
        return store(ctx).activity(webhook_token, since=since, limit=limit)

    @mcp.tool(annotations=READ)
    def search_requests(ctx: Context, webhook_token: str, query: str,
                        request_type: Kind | None = None, limit: int = 50, page: int = 1) -> dict:
        """Search captured bodies, URLs, and headers for a literal substring."""
        return store(ctx).requests(webhook_token, query=query, request_type=request_type, limit=limit, page=page)

    @mcp.tool(annotations=READ)
    def get_request(ctx: Context, webhook_token: str, request_id: str | None = None) -> dict:
        """Read a complete event; omit request_id to inspect the newest one."""
        return store(ctx).request(webhook_token, request_id)

    @mcp.tool(annotations=WRITE)
    def update_request(ctx: Context, webhook_token: str, request_id: str, note: str) -> dict:
        """Annotate an event without changing its original captured body."""
        return store(ctx).update_request(webhook_token, request_id, note)

    @mcp.tool(annotations=READ)
    def download_request_file(ctx: Context, webhook_token: str, request_id: str) -> dict:
        """Retrieve exact captured bytes as base64, including binary bodies or raw MIME."""
        event = store(ctx).request(webhook_token, request_id)["request"]
        return {"request_id": request_id, "body_base64": event["body_base64"], "encoding": "base64"}

    @mcp.tool(annotations=DELETE)
    def delete_request(ctx: Context, webhook_token: str, request_id: str) -> dict:
        """Permanently delete one event belonging to this inbox."""
        return store(ctx).delete_requests(webhook_token, request_id)

    @mcp.tool(annotations=DELETE)
    def delete_all_requests(ctx: Context, webhook_token: str) -> dict:
        """Clear stored events, keeping the inbox's addresses and settings."""
        return store(ctx).delete_requests(webhook_token)

    @mcp.tool(annotations=READ)
    def export_webhook_data(ctx: Context, webhook_token: str, format: Literal["json", "csv"] = "json", since: int = 0) -> dict:
        """Export a bounded page of full events; resume with next_since. Browser export streams the entire inbox."""
        result = store(ctx).requests(webhook_token, limit=25, oldest=True, since=since, full=True)
        events = []
        size = 0
        for event in result["requests"]:
            encoded_size = len(json.dumps(event).encode())
            if events and size + encoded_size > 4_194_304:
                break
            size += encoded_size
            events.append(event)
        metadata = {"count": len(events), "next_since": events[-1]["sorting"] if events else since,
                    "has_more": len(events) < result["total_requests"]}
        if format == "json":
            return {"format": "json", "requests": events, **metadata}
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "created_at", "type", "method", "url", "content", "note"])
        for event in events:
            cells = [event[key] for key in ["uuid", "created_at", "type", "method", "url", "content", "note"]]
            writer.writerow(["'" + str(cell) if str(cell).startswith(("=", "+", "-", "@")) else cell for cell in cells])
        return {"format": "csv", "content": output.getvalue(), **metadata}

    @mcp.tool(annotations=READ)
    async def wait_for_request(ctx: Context, webhook_token: str, timeout_seconds: float = 60,
                               request_type: Kind | None = None, since: int | None = None,
                               return_existing: bool = False) -> dict:
        """Wait up to 120 seconds; pass next_since when reconnecting to avoid missing events."""
        return await store(ctx).wait(webhook_token, timeout_seconds, request_type, since, return_existing)

    @mcp.tool(annotations=READ)
    async def wait_for_email(ctx: Context, webhook_token: str, timeout_seconds: float = 60,
                             since: int | None = None, return_existing: bool = False) -> dict:
        """Wait for an email received by Openhook's SMTP listener."""
        result = await store(ctx).wait(webhook_token, timeout_seconds, "email", since, return_existing)
        return {**result, "email": result["request"]}

    @mcp.tool(annotations=WRITE)
    def send_requests(ctx: Context, webhook_token: str, payloads: list[dict]) -> dict:
        """Create up to ten marked test HTTP events in this inbox."""
        if not 1 <= len(payloads) <= 10:
            raise InboxError("Send between one and ten test payloads.")
        inbox = store(ctx).info(webhook_token)
        events = [store(ctx).capture(inbox["inbox_id"], json.dumps(payload).encode(), url=inbox["url"],
                  headers={"content-type": ["application/json"]}, extra={"test_event": True}) for payload in payloads]
        return {"requests": events, "sent": len(events)}

    @mcp.tool(annotations=READ)
    def extract_links_from_request(ctx: Context, webhook_token: str, request_id: str | None = None) -> dict:
        """Extract HTTP links and verification codes without visiting the URLs."""
        return store(ctx).links(webhook_token, request_id)

    @mcp.tool(annotations=READ)
    def generate_oob_payloads(ctx: Context, webhook_token: str) -> dict:
        """Read callback addresses for authorized out-of-band testing."""
        inbox = store(ctx).info(webhook_token)
        return {key: inbox[key] for key in ("url", "email", "dns")}

    @mcp.tool(annotations=READ)
    def check_for_callbacks(ctx: Context, webhook_token: str, since: int = 0) -> dict:
        """Check for callbacks newer than a sequence cursor without waiting."""
        return store(ctx).requests(webhook_token, since=since)

    @mcp.tool(annotations=WRITE)
    async def respond_to_next_request(ctx: Context, webhook_token: str, content: str,
                                      status: int = 200, content_type: str = "text/plain",
                                      timeout_seconds: float = 60) -> dict:
        """Respond to the next request using ?openhook_wait=1, within its 20-second response window."""
        result = await store(ctx).wait(webhook_token, timeout_seconds, "web")
        if result["timeout"]:
            return result
        request = result["request"]
        if request.get("query", {}).get("openhook_wait") != ["1"]:
            raise InboxError("The request must opt into delayed responses with ?openhook_wait=1.")
        return store(ctx).set_response(webhook_token, request["uuid"], status, content, content_type)
