"""Machine-readable guides and schemas derived from the actual service."""

from __future__ import annotations

import json


def tools_markdown(tools) -> str:
    lines = ["# Openhook tool reference", "", f"{len(tools)} native tools. Generated with `uv run python scripts/generate_docs.py`.",
             "", "Keep private management tokens and provider credentials out of shared documents.", ""]
    for tool in sorted(tools, key=lambda item: item.name):
        lines.extend([f"## {tool.name}", "", tool.description or "", "", "```json",
                      json.dumps(tool.input_schema, indent=2), "```", ""])
    return "\n".join(lines)


def openapi_schema(origin, call_model, wait_model):
    # Request schemas come from the same Pydantic models that validate the API.
    components = {"WebCall": call_model.model_json_schema(), "WaitCall": wait_model.model_json_schema(),
                  "ExportCall": {"type": "object", "required": ["token"], "properties": {"token": {"type": "string"}}}}

    def post(operation, summary, model):
        return {"operationId": operation, "summary": summary,
                "requestBody": {"required": True, "content": {"application/json": {
                    "schema": {"$ref": "#/components/schemas/" + model}}}},
                "responses": {"200": {"description": "Successful response. call/wait wrap the result in data; export returns requests.",
                                      "content": {"application/json": {"schema": {"type": "object"}}}},
                              "400": {"description": "Invalid request"}, "401": {"description": "Invalid private token"},
                              "403": {"description": "Cross-origin request rejected"}, "404": {"description": "Inbox expired or not found"},
                              "413": {"description": "Request body exceeds limit"},
                              "429": {"description": "Rate or inbox limit reached; honor Retry-After when present"}}}

    paths = {
        "/api/call": {"post": post("callInbox", "Create, inspect, configure, or delete a webhook inbox", "WebCall")},
        "/api/wait": {"post": post("waitForEvent", "Wait with a cursor for an event (up to 30 seconds)", "WaitCall")},
        "/api/export": {"post": post("exportEvents", "Stream all retained events with original body bytes", "ExportCall")},
        "/api/tools": {"get": {"operationId": "listMcpTools", "summary": "Live MCP names and JSON input schemas",
                               "responses": {"200": {"description": "MCP tool catalog", "content": {"application/json": {"schema": {"type": "object"}}}}}}},
        "/health": {"get": {"operationId": "health", "summary": "Storage health and configured transport flags",
                            "responses": {"200": {"description": "Storage is reachable; not proof of public transport delivery"}}}},
    }
    paths["/api/call"]["post"]["description"] = (
        "Send action=create to obtain data.token and data.url. All other actions need the private token. "
        "Use get with request_id for full content, list with page for previews, send with payload for a marked test event, "
        "configure with config for response settings, rotate to replace the private token, activity with since/limit for durable history, and delete to remove the inbox. "
        "Never put a private token in a public URL. Tokens are in the JSON body, not an Authorization header.")
    paths["/api/wait"]["post"]["description"] = (
        "Use since=0 initially, then data.next_since after successful processing. "
        "Returns data.request (event or null), data.next_since, and data.timeout. "
        "This is an outbound long poll; it does not wake a stopped agent session.")
    capture = {"summary": "Receive an event at the public URL returned when creating an inbox",
               "parameters": [{"name": "identifier", "in": "path", "required": True,
                               "schema": {"type": "string", "format": "uuid"}}],
               "description": "Capture accepts incoming bodies, not private read access. Keep the private token out of this URL. Optional signature verification and configured HTTP response apply.",
               "responses": {"200": {"description": "Default acknowledgement; response status/content are configurable"},
                             "401": {"description": "Signature verification failed"}, "404": {"description": "Inbox missing or expired"},
                             "413": {"description": "Body too large"}, "429": {"description": "Rate limit reached"}}}
    paths["/h/{identifier}"] = {method: {**capture, "operationId": "capture" + method.title()}
                               for method in ("get", "head", "post", "put", "patch", "delete", "options")}
    return {"openapi": "3.1.1", "info": {"title": "Openhook native API", "version": "0.1.0",
            "description": "Webhook inboxes for agents. For MCP use the Streamable HTTP endpoint /mcp. Each inbox has its own private management token.",
            "license": {"name": "MIT", "identifier": "MIT"}}, "servers": [{"url": origin}], "paths": paths,
            "components": {"schemas": components}, "externalDocs": {"url": origin + "/agents.md"}}
