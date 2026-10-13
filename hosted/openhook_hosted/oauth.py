"""GitHub identity exchange for hosted browser sign-in."""

import httpx

from openhook.errors import InboxError


async def github_identity(settings, code: str, verifier: str) -> dict:
    """Exchange once and discard the provider credential after reading identity."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False) as client:
            response = await client.post("https://github.com/login/oauth/access_token", headers={"Accept": "application/json"}, data={
                "client_id": settings.github_client_id, "client_secret": settings.github_client_secret,
                "code": code, "code_verifier": verifier, "redirect_uri": settings.origin + "/auth/github/callback"})
            response.raise_for_status()
            payload = response.json()
            access_token = payload.get("access_token") if isinstance(payload, dict) else None
            if not access_token:
                raise InboxError("GitHub sign-in was not completed. Start again.", 400)
            response = await client.get("https://api.github.com/user", headers={
                "Accept": "application/vnd.github+json", "Authorization": "Bearer " + access_token})
            response.raise_for_status()
            identity = response.json()
            if not isinstance(identity, dict):
                raise ValueError("Invalid identity")
            return identity
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        if isinstance(exc, InboxError):
            raise
        raise InboxError("GitHub sign-in is temporarily unavailable. Try again.", 502) from None
