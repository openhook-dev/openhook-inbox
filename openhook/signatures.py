"""Webhook verification shared by capture and optional hosted billing."""

import hashlib
import hmac
import time

from openhook.errors import InboxError


def verify_signature(body: bytes, signature: str, secret: str) -> None:
    values = [value.strip().partition("=") for value in signature.split(",")]
    sent = next((value for key, _, value in values if key == "t"), "")
    try:
        if not secret or abs(time.time() - int(sent)) > 300:
            raise ValueError
    except ValueError:
        raise InboxError("Invalid or expired Stripe signature.", 401) from None
    expected = hmac.new(secret.encode(), sent.encode() + b"." + body, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(value, expected) for key, _, value in values if key == "v1"):
        raise InboxError("Invalid Stripe signature.", 401)
