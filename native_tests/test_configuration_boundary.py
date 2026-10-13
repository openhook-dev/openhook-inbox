"""Provider credentials are only read by explicitly enabled hosted services."""

import os

import pytest

from openhook.settings import Settings
from openhook_hosted.settings import HostedSettings


@pytest.fixture
def env_reads(monkeypatch):
    original = os.getenv
    reads = []

    def read(name, default=None):
        reads.append(name)
        return original(name, default)

    monkeypatch.setattr(os, "getenv", read)
    for key in list(os.environ):
        if key.startswith("OPENHOOK_"):
            monkeypatch.delenv(key)
    return reads


def test_core_does_not_read_or_hold_hosted_credentials(monkeypatch, env_reads):
    monkeypatch.setenv("OPENHOOK_HOSTED", "true")
    monkeypatch.setenv("OPENHOOK_POLAR_ACCESS_TOKEN", "operator-secret")
    settings = Settings.from_env()
    assert not settings.hosted_enabled
    assert not settings.billing_ready
    assert not hasattr(settings, "polar_access_token")
    assert not any(name.startswith(("OPENHOOK_GITHUB_", "OPENHOOK_POLAR_", "OPENHOOK_STRIPE_", "OPENHOOK_BILLING_")) for name in env_reads)


def test_disabled_hosted_does_not_read_credentials(monkeypatch, env_reads):
    monkeypatch.setenv("OPENHOOK_POLAR_ACCESS_TOKEN", "operator-secret")
    settings = HostedSettings.from_env()
    assert not settings.hosted_enabled
    assert not settings.polar_access_token
    assert not any(name.startswith(("OPENHOOK_GITHUB_", "OPENHOOK_POLAR_", "OPENHOOK_STRIPE_", "OPENHOOK_BILLING_")) for name in env_reads)


@pytest.mark.parametrize("provider,other", [("polar", "stripe"), ("stripe", "polar")])
def test_hosted_loads_only_selected_provider_with_sales_paused(monkeypatch, env_reads, provider, other):
    monkeypatch.setenv("OPENHOOK_HOSTED", "true")
    monkeypatch.setenv("OPENHOOK_BILLING_ENABLED", "false")
    monkeypatch.setenv("OPENHOOK_BILLING_PROVIDER", provider)
    monkeypatch.setenv("OPENHOOK_GITHUB_CLIENT_ID", "client")
    monkeypatch.setenv("OPENHOOK_GITHUB_CLIENT_SECRET", "login-secret")
    for suffix in ("ACCESS_TOKEN", "WEBHOOK_SECRET", "ORGANIZATION_ID", "PRODUCT_ID", "PRICE_ID", "SECRET_KEY"):
        monkeypatch.setenv(f"OPENHOOK_{provider.upper()}_{suffix}",
                           "operator-secret" if suffix in {"ACCESS_TOKEN", "WEBHOOK_SECRET", "SECRET_KEY"} else "public-id")
    settings = HostedSettings.from_env()
    assert settings.billing_configured  # Reconciliation remains enabled when new sales stop.
    assert not settings.billing_ready
    assert settings.github_client_secret == "login-secret"
    assert not any(name.startswith(f"OPENHOOK_{other.upper()}_") for name in env_reads)
    assert "operator-secret" not in repr(settings)
    assert "login-secret" not in repr(settings)


def test_invalid_hosted_provider_fails_before_reading_credentials(monkeypatch, env_reads):
    monkeypatch.setenv("OPENHOOK_HOSTED", "true")
    monkeypatch.setenv("OPENHOOK_BILLING_PROVIDER", "invalid")
    with pytest.raises(ValueError, match="must be stripe or polar"):
        HostedSettings.from_env()
    assert "OPENHOOK_GITHUB_CLIENT_SECRET" not in env_reads
