"""Core configuration: no hosted login or payment credentials."""

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
    hosted_enabled: bool = field(default=False, init=False)
    support_email: str = ""
    umami_script_url: str = ""
    umami_website_id: str = ""
    metrics_token: str = field(default="", repr=False)

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
            support_email=os.getenv("OPENHOOK_SUPPORT_EMAIL", ""),
            umami_script_url=os.getenv("OPENHOOK_UMAMI_SCRIPT_URL", ""),
            umami_website_id=os.getenv("OPENHOOK_UMAMI_WEBSITE_ID", ""),
            metrics_token=os.getenv("OPENHOOK_METRICS_TOKEN", ""),
            storage_limit=int(os.getenv("OPENHOOK_STORAGE_LIMIT", cls.storage_limit)),
        )

    @property
    def billing_ready(self) -> bool:
        return False

    @property
    def billing_provider_label(self) -> str:
        return ""

    def prepare(self) -> None:
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
