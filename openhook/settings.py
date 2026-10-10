"""Explicit configuration shared by HTTP, MCP, SMTP, and DNS."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    origin: str = "http://127.0.0.1:8788"
    database: str = "data/openhook.sqlite3"
    email_domain: str = ""
    dns_domain: str = ""
    dns_address: str = "127.0.0.1"
    smtp_port: int = 2525
    dns_port: int = 5353
    body_limit: int = 1_048_576
    event_limit: int = 1000
    inbox_limit: int = 10000
    storage_limit: int = 1_073_741_824
    hosted_enabled: bool = False
    github_client_id: str = ""
    github_client_secret: str = field(default="", repr=False)
    billing_enabled: bool = False
    stripe_secret_key: str = field(default="", repr=False)
    stripe_webhook_secret: str = field(default="", repr=False)
    stripe_price_id: str = ""
    stripe_live: bool = False

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            origin=os.getenv("OPENHOOK_ORIGIN", cls.origin).rstrip("/"),
            database=os.getenv("OPENHOOK_DATABASE", cls.database),
            email_domain=os.getenv("OPENHOOK_EMAIL_DOMAIN", "").lower().strip("."),
            dns_domain=os.getenv("OPENHOOK_DNS_DOMAIN", "").lower().strip("."),
            dns_address=os.getenv("OPENHOOK_DNS_ADDRESS", cls.dns_address),
            smtp_port=int(os.getenv("OPENHOOK_SMTP_PORT", cls.smtp_port)),
            dns_port=int(os.getenv("OPENHOOK_DNS_PORT", cls.dns_port)),
            hosted_enabled=os.getenv("OPENHOOK_HOSTED", "").lower() in {"1", "true"},
            github_client_id=os.getenv("OPENHOOK_GITHUB_CLIENT_ID", ""),
            github_client_secret=os.getenv("OPENHOOK_GITHUB_CLIENT_SECRET", ""),
            billing_enabled=os.getenv("OPENHOOK_BILLING_ENABLED", "").lower() in {"1", "true"},
            stripe_secret_key=os.getenv("OPENHOOK_STRIPE_SECRET_KEY", ""),
            stripe_webhook_secret=os.getenv("OPENHOOK_STRIPE_WEBHOOK_SECRET", ""),
            stripe_price_id=os.getenv("OPENHOOK_STRIPE_PRICE_ID", ""),
            stripe_live=os.getenv("OPENHOOK_STRIPE_LIVE", "").lower() in {"1", "true"},
            storage_limit=int(os.getenv("OPENHOOK_STORAGE_LIMIT", cls.storage_limit)),
        )

    def prepare(self) -> None:
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
