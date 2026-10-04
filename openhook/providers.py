"""Register source subscriptions; capture and delivery remain native Openhook."""

from __future__ import annotations

import re
import secrets
from urllib.parse import urlsplit

import httpx

from openhook.store import InboxError, Store

PROVIDERS = {"github", "stripe", "linear"}
LINEAR_CREATE = "mutation Create($input: WebhookCreateInput!) { webhookCreate(input: $input) { success webhook { id secret } } }"
LINEAR_DELETE = "mutation Delete($id: String!) { webhookDelete(id: $id) { success } }"


def credentials(value: str) -> str:
    if not value or len(value) > 4096 or any(character.isspace() for character in value):
        raise InboxError("Supply a valid provider access token.")
    return value


def repository_name(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise InboxError("Repository must be owner/repo.")
    return value


def checked(response: httpx.Response, provider: str) -> dict:
    if not response.is_success:
        raise InboxError(f"{provider.title()} registration failed (HTTP {response.status_code}). Check credentials and webhook permissions.")
    data = response.json()
    if not isinstance(data, dict) or data.get("errors"):
        raise InboxError(f"{provider.title()} refused the operation. Check webhook permissions and event types.")
    return data


async def register(store: Store, provider: str, access_token: str, events: list[str], target: str = "") -> dict:
    access_token = credentials(access_token)
    if provider not in PROVIDERS or not 1 <= len(events) <= 100 or any(not event or len(event) > 100 for event in events):
        raise InboxError("Supply a supported provider and between one and 100 event types.")
    origin = urlsplit(store.settings.origin)
    if origin.scheme != "https" or origin.hostname in {"localhost", "127.0.0.1"}:
        raise InboxError("Provider registration needs a deployment with a public HTTPS origin.")
    if provider == "github":
        target = repository_name(target)
    inbox = store.create(name=f"{provider}: {target or 'events'}"[:60], config={"enabled": False})
    remote_id = None
    secret = secrets.token_urlsafe(32)
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=False, trust_env=False) as client:
            if provider == "github":
                store.configure(inbox["token"], {"signature_provider": "github", "verification_secret": secret, "enabled": True})
                response = await client.post(f"https://api.github.com/repos/{target}/hooks",
                    headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
                    json={"name": "web", "active": True, "events": events,
                          "config": {"url": inbox["url"], "content_type": "json", "secret": secret, "insecure_ssl": "0"}})
                data = checked(response, provider)
                remote_id = str(data["id"])
            elif provider == "stripe":
                response = await client.post("https://api.stripe.com/v1/webhook_endpoints",
                    headers={"Authorization": f"Bearer {access_token}"},
                    data={"url": inbox["url"], "enabled_events[]": events, "description": "Openhook agent inbox"})
                data = checked(response, provider)
                remote_id, secret = str(data["id"]), data["secret"]
            else:
                payload = {"url": inbox["url"], "resourceTypes": events, "label": "Openhook agent inbox"}
                payload.update({"teamId": target} if target else {"allPublicTeams": True})
                response = await client.post("https://api.linear.app/graphql", headers={"Authorization": access_token},
                                             json={"query": LINEAR_CREATE, "variables": {"input": payload}})
                data = checked(response, provider)["data"]["webhookCreate"]
                if not data["success"]:
                    raise InboxError("Linear refused webhook creation.")
                remote_id, secret = str(data["webhook"]["id"]), data["webhook"]["secret"]
            if not secret:
                raise InboxError("The provider did not return a signing secret.")
            store.configure(inbox["token"], {"signature_provider": provider, "verification_secret": secret, "enabled": True})
            store.attach_subscription(inbox["token"], provider, remote_id, target)
        return {**store.info(inbox["token"]), "events": events,
                "cleanup": "Unregister with unregister_webhook before the inbox expires. Provider subscriptions do not automatically expire."}
    except BaseException:
        # Credentials are used only for this call, including best-effort rollback.
        if remote_id:
            try:
                await remove(provider, access_token, remote_id, target)
            except Exception:
                pass
        store.delete(inbox["token"])
        raise


async def remove(provider: str, access_token: str, remote_id: str, target: str) -> None:
    access_token = credentials(access_token)
    async with httpx.AsyncClient(timeout=20, follow_redirects=False, trust_env=False) as client:
        if provider == "github":
            if not remote_id.isdigit():
                raise InboxError("Invalid GitHub subscription ID.")
            response = await client.delete(f"https://api.github.com/repos/{repository_name(target)}/hooks/{remote_id}",
                                            headers={"Authorization": f"Bearer {access_token}"})
        elif provider == "stripe":
            if not re.fullmatch(r"we_[A-Za-z0-9]+", remote_id):
                raise InboxError("Invalid Stripe subscription ID.")
            response = await client.delete(f"https://api.stripe.com/v1/webhook_endpoints/{remote_id}",
                                            headers={"Authorization": f"Bearer {access_token}"})
        elif provider == "linear":
            response = await client.post("https://api.linear.app/graphql", headers={"Authorization": access_token},
                json={"query": LINEAR_DELETE, "variables": {"id": remote_id}})
            data = checked(response, provider)
            if not data["data"]["webhookDelete"]["success"]:
                raise InboxError("Linear did not remove the subscription.")
        else:
            raise InboxError("Unsupported provider.")
        if not response.is_success and response.status_code != 404:
            raise InboxError(f"{provider.title()} subscription removal failed (HTTP {response.status_code}).")
