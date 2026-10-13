"""Operator credentials for the optional hosted service only."""

import os
from dataclasses import asdict, dataclass, field

from openhook.settings import Settings


@dataclass(frozen=True)
class HostedSettings(Settings):
    hosted_enabled: bool = False
    github_client_id: str = ""
    github_client_secret: str = field(default="", repr=False)
    billing_enabled: bool = False
    billing_provider: str = "stripe"
    polar_access_token: str = field(default="", repr=False)
    polar_webhook_secret: str = field(default="", repr=False)
    polar_organization_id: str = ""
    polar_product_id: str = ""
    polar_price_id: str = ""
    polar_sandbox: bool = True
    stripe_secret_key: str = field(default="", repr=False)
    stripe_webhook_secret: str = field(default="", repr=False)
    stripe_price_id: str = ""
    stripe_live: bool = False

    @classmethod
    def from_env(cls):
        core = asdict(Settings.from_env())
        core["hosted_enabled"] = os.getenv("OPENHOOK_HOSTED", "").lower() in {"1", "true"}
        if not core["hosted_enabled"]:
            return cls(**core)
        provider = os.getenv("OPENHOOK_BILLING_PROVIDER", "stripe")
        if provider not in {"stripe", "polar"}:
            raise ValueError("OPENHOOK_BILLING_PROVIDER must be stripe or polar.")
        values = dict(
            github_client_id=os.getenv("OPENHOOK_GITHUB_CLIENT_ID", ""),
            github_client_secret=os.getenv("OPENHOOK_GITHUB_CLIENT_SECRET", ""),
            billing_enabled=os.getenv("OPENHOOK_BILLING_ENABLED", "").lower() in {"1", "true"},
            billing_provider=provider,
        )
        if provider == "polar":
            values.update(
                polar_access_token=os.getenv("OPENHOOK_POLAR_ACCESS_TOKEN", ""),
                polar_webhook_secret=os.getenv("OPENHOOK_POLAR_WEBHOOK_SECRET", ""),
                polar_organization_id=os.getenv("OPENHOOK_POLAR_ORGANIZATION_ID", ""),
                polar_product_id=os.getenv("OPENHOOK_POLAR_PRODUCT_ID", ""),
                polar_price_id=os.getenv("OPENHOOK_POLAR_PRICE_ID", ""),
                polar_sandbox=os.getenv("OPENHOOK_POLAR_SANDBOX", "true").lower() in {"1", "true"},
            )
        else:
            values.update(
                stripe_secret_key=os.getenv("OPENHOOK_STRIPE_SECRET_KEY", ""),
                stripe_webhook_secret=os.getenv("OPENHOOK_STRIPE_WEBHOOK_SECRET", ""),
                stripe_price_id=os.getenv("OPENHOOK_STRIPE_PRICE_ID", ""),
                stripe_live=os.getenv("OPENHOOK_STRIPE_LIVE", "").lower() in {"1", "true"},
            )
        return cls(**core, **values)

    @property
    def billing_configured(self) -> bool:
        if self.billing_provider == "polar":
            credentials = (self.polar_access_token, self.polar_webhook_secret,
                           self.polar_organization_id, self.polar_product_id, self.polar_price_id)
        elif self.billing_provider == "stripe":
            credentials = (self.stripe_secret_key, self.stripe_price_id, self.stripe_webhook_secret)
        else:
            return False
        return self.hosted_enabled and all(credentials)

    @property
    def billing_ready(self) -> bool:
        return bool(self.billing_enabled and self.billing_configured
                    and self.github_client_id and self.github_client_secret)

    @property
    def billing_provider_label(self) -> str:
        return "Polar" if self.billing_provider == "polar" else "Stripe"
