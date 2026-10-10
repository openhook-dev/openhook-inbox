"""Browser account endpoints for opt-in hosted deployments."""

from __future__ import annotations

from urllib.parse import urlencode

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route

from openhook.accounts import Accounts, OAUTH_SECONDS, SESSION_SECONDS, github_identity
from openhook.store import InboxError
from openhook.billing import Billing


class KeyCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=60)


class InboxCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(default="", max_length=60)


def cookie_name(settings, kind: str) -> str:
    prefix = "__Host-" if settings.origin.startswith("https://") else ""
    return prefix + "openhook-" + kind


def set_cookie(response, settings, kind, value, age):
    response.set_cookie(cookie_name(settings, kind), value, max_age=age, httponly=True,
                        secure=settings.origin.startswith("https://"), samesite="lax", path="/")


def accounts(request) -> Accounts:
    service = request.app.state.accounts
    if service is None:
        raise InboxError("Hosted accounts are not enabled on this deployment.", 404)
    return service


def require_browser_origin(request):
    if request.headers.get("origin") != request.app.state.store.settings.origin:
        raise InboxError("Open this page on the configured Openhook origin and try again.", 403)


def signed_in(request) -> dict:
    settings = request.app.state.store.settings
    return accounts(request).session(request.cookies.get(cookie_name(settings, "session"), ""))


def error_response(exc):
    return JSONResponse({"success": False, "message": str(exc)}, status_code=exc.status)


async def account_status(request):
    try:
        service = accounts(request)
        settings = service.store.settings
        configured = bool(settings.github_client_id and settings.github_client_secret)
        token = request.cookies.get(cookie_name(settings, "session"), "")
        try:
            account = service.session(token)
        except InboxError:
            account = None
        return JSONResponse({"success": True, "data": {
            "sign_in_available": configured, "account": account,
            "keys": service.keys(account["id"]) if account else [],
            "usage": service.usage(account["id"]) if account else None,
            "inboxes": service.inboxes(account["id"]) if account else [],
            "billing_available": Billing(service.store).available,
            "billing_management_available": Billing(service.store).configured,
            "billing_customer": bool(Billing(service.store).entitlement(account["id"]).get("customer_id")) if account else False,
        }})
    except InboxError as exc:
        return error_response(exc)


async def github_start(request):
    try:
        service = accounts(request)
        settings = service.store.settings
        if not settings.github_client_id or not settings.github_client_secret:
            raise InboxError("Hosted sign-in is not configured yet.", 503)
        state, challenge = service.begin_login()
        params = {"client_id": settings.github_client_id, "redirect_uri": settings.origin + "/auth/github/callback",
                  "scope": "read:user", "state": state, "code_challenge": challenge, "code_challenge_method": "S256"}
        response = RedirectResponse("https://github.com/login/oauth/authorize?" + urlencode(params), status_code=303)
        set_cookie(response, settings, "oauth", state, OAUTH_SECONDS)
        return response
    except InboxError as exc:
        return error_response(exc)


async def github_callback(request):
    settings = request.app.state.store.settings
    try:
        service = accounts(request)
        verifier = service.consume_login(request.query_params.get("state", ""),
                                         request.cookies.get(cookie_name(settings, "oauth"), ""))
        code = request.query_params.get("code", "")
        if not code or len(code) > 1024 or not settings.github_client_id or not settings.github_client_secret:
            raise InboxError("GitHub sign-in was not completed. Start again.", 400)
        identity = await github_identity(settings, code, verifier)
        _, token = service.sign_in(identity.get("id"), identity.get("login"))
        response = RedirectResponse("/account", status_code=303)
        set_cookie(response, settings, "session", token, SESSION_SECONDS)
    except InboxError as exc:
        response = error_response(exc)
    response.delete_cookie(cookie_name(settings, "oauth"), path="/", secure=settings.origin.startswith("https://"), httponly=True, samesite="lax")
    return response


async def sign_out(request):
    try:
        require_browser_origin(request)
        service = accounts(request)
        settings = service.store.settings
        service.sign_out(request.cookies.get(cookie_name(settings, "session"), ""))
        response = JSONResponse({"success": True})
        response.delete_cookie(cookie_name(settings, "session"), path="/", secure=settings.origin.startswith("https://"), httponly=True, samesite="lax")
        return response
    except InboxError as exc:
        return error_response(exc)


async def create_key(request):
    try:
        require_browser_origin(request)
        account = signed_in(request)
        call = KeyCall.model_validate(await request.json())
        result = accounts(request).create_key(account["id"], call.name)
        return JSONResponse({"success": True, "data": result}, status_code=201)
    except InboxError as exc:
        return error_response(exc)
    except (ValidationError, ValueError):
        return error_response(InboxError("Name the key using 1 to 60 characters."))


async def revoke_key(request):
    try:
        require_browser_origin(request)
        account = signed_in(request)
        accounts(request).revoke_key(account["id"], request.path_params["identifier"])
        return JSONResponse({"success": True})
    except InboxError as exc:
        return error_response(exc)


def inbox_account(request):
    """Agent keys can manage inboxes, but never browser sessions, keys or billing."""
    authorization = request.headers.get("authorization", "")
    if authorization:
        if not authorization.startswith("Bearer "):
            raise InboxError("Supply a hosted agent key as a Bearer token.", 401)
        return accounts(request).authenticate_key(authorization[7:])
    if request.method != "GET":
        require_browser_origin(request)
    return signed_in(request)


async def hosted_inboxes(request):
    try:
        account = inbox_account(request)
        service = accounts(request)
        if request.method == "GET":
            return JSONResponse({"success": True, "data": {"inboxes": service.inboxes(account["id"]), "usage": service.usage(account["id"])}})
        call = InboxCall.model_validate(await request.json())
        inbox = service.store.create(name=call.name, account=account["id"])
        return JSONResponse({"success": True, "data": inbox}, status_code=201)
    except InboxError as exc:
        return error_response(exc)
    except (ValidationError, ValueError):
        return error_response(InboxError("Supply a name of up to 60 characters."))


async def hosted_inbox_access(request):
    try:
        account = inbox_account(request)
        result = accounts(request).inbox_access(account["id"], request.path_params["identifier"])
        return JSONResponse({"success": True, "data": result})
    except InboxError as exc:
        return error_response(exc)


async def billing_redirect(request):
    try:
        if request.path_params["action"] not in {"checkout", "portal"}:
            raise InboxError("Billing action not found.", 404)
        require_browser_origin(request)
        account = signed_in(request)
        billing = Billing(accounts(request).store)
        url = await (billing.checkout(account["id"]) if request.path_params["action"] == "checkout" else billing.portal(account["id"]))
        return JSONResponse({"success": True, "data": {"url": url}})
    except InboxError as exc:
        return error_response(exc)


async def billing_webhook(request):
    try:
        result = await Billing(accounts(request).store).receive(await request.body(), request.headers.get("stripe-signature", ""))
        return JSONResponse({"success": True, "data": result})
    except InboxError as exc:
        return error_response(exc)


ROUTES = [
    Route("/billing/stripe", billing_webhook, methods=["POST"]),
    Route("/api/account/billing/{action}", billing_redirect, methods=["POST"]),
    Route("/auth/github", github_start), Route("/auth/github/callback", github_callback),
    Route("/api/account", account_status), Route("/api/account/sign-out", sign_out, methods=["POST"]),
    Route("/api/account/keys", create_key, methods=["POST"]),
    Route("/api/account/keys/{identifier}/revoke", revoke_key, methods=["POST"]),
    Route("/api/account/inboxes", hosted_inboxes, methods=["GET", "POST"]),
    Route("/api/account/inboxes/{identifier}/access", hosted_inbox_access, methods=["POST"]),
]
