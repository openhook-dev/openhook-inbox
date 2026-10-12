"""Recoverable HTTP errors without changing existing clients' message field."""

from http import HTTPStatus

from starlette.responses import HTMLResponse, JSONResponse, Response

from openhook.pages import prefers_markdown


RESOLUTIONS = {
    400: "Check the request fields against /openapi.json and retry with valid JSON.",
    401: "Use your private inbox token or the authentication described in /docs.",
    402: "Review /pricing and manage your hosted subscription at /account.",
    403: "Use the configured Openhook origin and an account authorized for this operation.",
    404: "Check /docs, /sitemap.xml or /llms.txt. An inbox may have expired or been deleted.",
    405: "Use a method listed for this endpoint in /openapi.json.",
    413: "Reduce the request body to no more than 1 MiB.",
    429: "Honor Retry-After when present. Check inbox and account capacity before retrying.",
    500: "Retry with backoff. If the problem persists, use the support contact on /contact.",
    503: "Retry later with backoff and check /health before repeating the operation.",
}


def problem(status, detail, *, headers=None):
    title = HTTPStatus(status).phrase
    return JSONResponse({"type": "about:blank", "title": title, "status": status,
                         "code": title.lower().replace(" ", "_"), "detail": detail,
                         "resolution": RESOLUTIONS.get(status, "Consult /docs for the supported API contract."),
                         "success": False, "message": detail}, status_code=status,
                        media_type="application/problem+json", headers={"Cache-Control": "no-store", **(headers or {})})


async def http_error(request, exc):
    status = getattr(exc, "status_code", 500)
    headers = getattr(exc, "headers", None)
    detail = HTTPStatus(status).phrase  # Do not echo arbitrary URLs, inputs, or exception text.
    if request.url.path.startswith(("/api", "/h/", "/billing/", "/auth/")):
        return problem(status, detail, headers=headers)
    resolution = RESOLUTIONS.get(status, "See /docs for the supported routes.")
    response_headers = {"Vary": "Accept", "Cache-Control": "no-store", "X-Robots-Tag": "noindex", **(headers or {})}
    if prefers_markdown(request.headers.get("accept", "")):
        return Response(f"# {status}: {detail}\n\n{resolution}\n\n[Documentation](/docs) · [Site map](/sitemap.xml) · [Agent guide](/llms.txt)\n",
                        status_code=status, media_type="text/markdown", headers=response_headers)
    return HTMLResponse(f'<!doctype html><html lang="en"><head><title>{status} — Openhook</title>'
                        '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body><main>'
                        f'<h1>{status}: {detail}</h1><p>{resolution}</p><p><a href="/">Openhook home</a> · '
                        '<a href="/docs">Documentation</a> · <a href="/llms.txt">Agent guide</a></p></main></body></html>',
                        status_code=status, headers=response_headers)
