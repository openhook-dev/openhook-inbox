"""Channel service configuration. No third-party account credentials."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    origin: str = "http://127.0.0.1:8788"
    database: str = "data/openhook.sqlite3"
    channel_limit: int = 1000
    body_limit: int = 1_048_576
    storage_limit: int = 1_073_741_824
    support_email: str = ""
    umami_script_url: str = ""
    umami_website_id: str = ""
    metrics_token: str = field(default="", repr=False)

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            origin=os.getenv("OPENHOOK_ORIGIN", cls.origin).rstrip("/"),
            database=os.getenv("OPENHOOK_DATABASE", cls.database),
            support_email=os.getenv("OPENHOOK_SUPPORT_EMAIL", ""),
            umami_script_url=os.getenv("OPENHOOK_UMAMI_SCRIPT_URL", ""),
            umami_website_id=os.getenv("OPENHOOK_UMAMI_WEBSITE_ID", ""),
            metrics_token=os.getenv("OPENHOOK_METRICS_TOKEN", ""),
            channel_limit=int(os.getenv("OPENHOOK_CHANNEL_LIMIT", cls.channel_limit)),
            storage_limit=int(os.getenv("OPENHOOK_STORAGE_LIMIT", cls.storage_limit)),
        )

    def prepare(self) -> None:
        Path(self.database).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
