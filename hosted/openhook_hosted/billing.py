"""Opt-in Stripe billing. Only verified paid invoices extend hosted access.

Checkout uses durable idempotency keys. Payment deliveries are recorded in the
same SQLite transaction as entitlements, so retries cannot grant twice.
"""

from __future__ import annotations

import json
import time
from urllib.parse import quote, urlsplit
from uuid import uuid4

import httpx

from openhook.errors import InboxError
from openhook.hosted_store import PRO_RETENTION_SECONDS
from openhook.signatures import verify_signature

STRIPE_VERSION = "2025-06-30.basil"


class BillingBase:
    def __init__(self, store):
        self.store = store
        self.settings = store.settings

    @property
    def configured(self):
        return self.settings.billing_configured

    @property
    def available(self):
        return self.configured and self.settings.billing_enabled

    def require_configured(self):
        if not self.configured:
            raise InboxError("Hosted billing is not configured yet.", 503)

    def require_available(self):
        if not self.available:
            raise InboxError("Hosted billing is not available yet.", 503)

    def entitlement(self, account):
        with self.store.connection() as db:
            row = db.execute("SELECT * FROM hosted_entitlements WHERE account=?", (account,)).fetchone()
        return dict(row) if row else {}

    @staticmethod
    def redirect_url(result, hostname):
        url = result.get("url", "")
        if not isinstance(url, str) or urlsplit(url).scheme != "https" or urlsplit(url).hostname != hostname:
            raise InboxError("Invalid billing redirect response.", 502)
        return url


class Billing(BillingBase):
    """Stripe adapter retained for existing self-hosted deployments."""

    async def api(self, method, path, data=None, *, key=None):
        self.require_configured()
        headers = {"Authorization": "Bearer " + self.settings.stripe_secret_key, "Stripe-Version": STRIPE_VERSION}
        if key:
            headers["Idempotency-Key"] = key
        try:
            async with httpx.AsyncClient(timeout=20, trust_env=False, follow_redirects=False) as client:
                response = await client.request(method, "https://api.stripe.com/v1/" + path, data=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                if not isinstance(result, dict):
                    raise ValueError
                return result
        except (httpx.HTTPError, ValueError):
            # Never expose provider response bodies, customer data, or credentials.
            raise InboxError("Billing is temporarily unavailable. Please retry shortly.", 502) from None

    async def customer(self, account):
        current = self.entitlement(account)
        if current.get("customer_id"):
            return current["customer_id"]
        # Keep an unresolved create stable even after Stripe's 24-hour key window.
        now = time.time()
        with self.store.connection(write=True) as db:
            db.execute("INSERT INTO hosted_entitlements(account,status,updated) VALUES(?,'creating_customer',?) ON CONFLICT DO NOTHING", (account, now))
            row = db.execute("SELECT * FROM hosted_entitlements WHERE account=?", (account,)).fetchone()
            if row["customer_id"]:
                return row["customer_id"]
            if row["updated"] < now - 23 * 3600:
                raise InboxError("Customer setup needs support before another payment attempt.", 409)
        result = await self.api("POST", "customers", {"metadata[openhook_account]": account}, key="openhook-customer-" + account)
        customer = result.get("id")
        if not isinstance(customer, str) or not customer.startswith("cus_"):
            raise InboxError("Invalid billing customer response.", 502)
        with self.store.connection(write=True) as db:
            db.execute("UPDATE hosted_entitlements SET customer_id=?,status='free',updated=? WHERE account=? AND customer_id IS NULL", (customer, now, account))
        return self.entitlement(account)["customer_id"]

    async def checkout(self, account):
        self.require_available()
        if self.entitlement(account).get("paid_until", 0) > time.time():
            raise InboxError("You already have Pro. Use Manage billing for your subscription.", 409)
        price = await self.api("GET", "prices/" + quote(self.settings.stripe_price_id, safe=""))
        recurring = price.get("recurring") or {}
        if not (price.get("active") is True and price.get("livemode") is self.settings.stripe_live
                and price.get("unit_amount") == 1900 and price.get("currency") == "usd"
                and price.get("billing_scheme") == "per_unit" and price.get("transform_quantity") is None
                and price.get("tax_behavior") == "exclusive"
                and recurring.get("interval") == "month" and recurring.get("interval_count") == 1
                and recurring.get("usage_type") == "licensed"):
            raise InboxError("The hosted price is not configured correctly.", 503)
        customer = await self.customer(account)
        subscriptions = await self.api("GET", "subscriptions?customer=" + quote(customer, safe="") + "&status=all&limit=100")
        if subscriptions.get("has_more") or any(s.get("status") not in {"canceled", "incomplete_expired"} for s in subscriptions.get("data", [])):
            raise InboxError("A subscription already exists. Use Manage billing or wait for payment confirmation.", 409)
        with self.store.connection(write=True) as db:
            db.execute("INSERT INTO billing_attempts(account,identifier,created) VALUES(?,?,?) ON CONFLICT DO NOTHING", (account, str(uuid4()), int(time.time())))
            attempt = dict(db.execute("SELECT * FROM billing_attempts WHERE account=?", (account,)).fetchone())
        if attempt["session_id"]:
            session = await self.api("GET", "checkout/sessions/" + quote(attempt["session_id"], safe=""))
            if session.get("status") == "open":
                return self.redirect_url(session, "checkout.stripe.com")
            ended_subscription = any(s.get("id") == session.get("subscription") and s.get("status") in {"canceled", "incomplete_expired"}
                                     for s in subscriptions.get("data", []))
            if session.get("status") != "expired" and not (session.get("status") == "complete" and ended_subscription):
                raise InboxError("Payment is being confirmed. Refresh your account shortly.", 409)
            with self.store.connection(write=True) as db:
                db.execute("UPDATE billing_attempts SET identifier=?,created=?,session_id=NULL,url=NULL WHERE account=? AND identifier=?", (str(uuid4()), int(time.time()), account, attempt["identifier"]))
                attempt = dict(db.execute("SELECT * FROM billing_attempts WHERE account=?", (account,)).fetchone())
        if attempt["created"] < time.time() - 23 * 3600:
            raise InboxError("An unresolved checkout needs support before another payment attempt.", 409)
        session = await self.api("POST", "checkout/sessions", {
            "customer": customer, "mode": "subscription", "client_reference_id": account,
            "subscription_data[metadata][openhook_account]": account,
            "line_items[0][price]": self.settings.stripe_price_id, "line_items[0][quantity]": "1",
            "success_url": self.settings.origin + "/account?checkout=complete",
            "cancel_url": self.settings.origin + "/account", "expires_at": str(attempt["created"] + 86400),
            "automatic_tax[enabled]": "true", "customer_update[address]": "auto",
            "billing_address_collection": "required", "consent_collection[terms_of_service]": "required",
        }, key="openhook-checkout-" + attempt["identifier"])
        url = self.redirect_url(session, "checkout.stripe.com")
        if not isinstance(session.get("id"), str) or not session["id"].startswith("cs_"):
            raise InboxError("Invalid checkout response.", 502)
        with self.store.connection(write=True) as db:
            db.execute("UPDATE billing_attempts SET session_id=?,url=? WHERE account=? AND identifier=?", (session["id"], url, account, attempt["identifier"]))
        return url

    async def portal(self, account):
        self.require_configured()
        customer = self.entitlement(account).get("customer_id")
        if not customer:
            raise InboxError("There is no billing account to manage yet.", 404)
        result = await self.api("POST", "billing_portal/sessions", {"customer": customer, "return_url": self.settings.origin + "/account"})
        return self.redirect_url(result, "billing.stripe.com")

    async def receive(self, body, signature):
        self.require_configured()
        verify_signature(body, signature, self.settings.stripe_webhook_secret)
        try:
            event = json.loads(body)
            identifier, kind, obj = event["id"], event["type"], event["data"]["object"]
            if not isinstance(identifier, str) or not identifier.startswith("evt_") or not isinstance(kind, str) or not isinstance(obj, dict):
                raise ValueError
            if event.get("livemode") is not self.settings.stripe_live:
                raise ValueError
        except (ValueError, KeyError, TypeError):
            raise InboxError("Invalid billing event.", 400) from None
        with self.store.connection() as db:
            if db.execute("SELECT 1 FROM billing_events WHERE id=?", (identifier,)).fetchone():
                return {"duplicate": True}
        # Non-payment events never grant or revoke already-paid time. Cancellations
        # and failed renewals stop access naturally at the verified paid-through date.
        if kind != "invoice.paid":
            return {"ignored": True}
        invoice_id = obj.get("id", "")
        if not isinstance(invoice_id, str) or not invoice_id.startswith("in_"):
            raise InboxError("Invalid invoice event.", 400)
        invoice = await self.api("GET", "invoices/" + quote(invoice_id, safe=""))
        customer = invoice.get("customer")
        with self.store.connection() as db:
            owner = db.execute("SELECT account FROM hosted_entitlements WHERE customer_id=?", (customer,)).fetchone()
        if not owner:
            return {"ignored": True}
        account = owner["account"]
        subscription_id = (invoice.get("parent") or {}).get("subscription_details", {}).get("subscription")
        if not isinstance(subscription_id, str) or not subscription_id.startswith("sub_"):
            raise InboxError("The invoice has no hosted subscription.", 400)
        subscription = await self.api("GET", "subscriptions/" + quote(subscription_id, safe=""))
        if (subscription.get("customer") != customer or subscription.get("metadata", {}).get("openhook_account") != account
                or invoice.get("livemode") is not self.settings.stripe_live or subscription.get("livemode") is not self.settings.stripe_live):
            raise InboxError("The invoice does not match this hosted account.", 400)
        lines = await self.api("GET", "invoices/" + quote(invoice_id, safe="") + "/lines?limit=100")
        matching = [line for line in lines.get("data", [])
                    if (line.get("pricing") or {}).get("price_details", {}).get("price") == self.settings.stripe_price_id
                    and (line.get("parent") or {}).get("subscription_item_details", {}).get("subscription") == subscription_id
                    and (line.get("parent") or {}).get("subscription_item_details", {}).get("proration") is False]
        if (invoice.get("status") != "paid" or invoice.get("amount_paid", 0) <= 0 or invoice.get("currency") != "usd"
                or lines.get("has_more") or len(matching) != 1 or matching[0].get("amount", 0) <= 0):
            raise InboxError("The invoice does not contain a paid hosted period.", 400)
        period_end = matching[0].get("period", {}).get("end")
        if type(period_end) is not int or period_end <= 0:
            raise InboxError("Invalid paid period.", 400)
        now = time.time()
        with self.store.connection(write=True) as db:
            if db.execute("SELECT 1 FROM billing_events WHERE id=?", (identifier,)).fetchone():
                return {"duplicate": True}
            inserted = db.execute("INSERT INTO paid_invoices VALUES(?,?,?,?,?,?,?) ON CONFLICT DO NOTHING",
                                  (invoice_id, account, subscription_id, period_end, invoice["amount_paid"], invoice["currency"], now)).rowcount
            if inserted:
                # MAX makes older invoices harmless even when delivered concurrently.
                db.execute("UPDATE hosted_entitlements SET subscription_id=CASE WHEN paid_until<? THEN ? ELSE subscription_id END, "
                           "paid_until=MAX(paid_until,?),status='paid',updated=? WHERE account=?",
                           (period_end, subscription_id, period_end, now, account))
                db.execute("UPDATE inboxes SET expires=MAX(expires,?) WHERE id IN (SELECT inbox FROM hosted_inboxes WHERE account=?)",
                           (period_end + PRO_RETENTION_SECONDS, account))
            db.execute("INSERT INTO billing_events VALUES(?,?,?)", (identifier, kind, now))
        return {"applied": bool(inserted)}


def billing_for(store):
    if store.settings.billing_provider == "polar":
        from openhook_hosted.polar_billing import PolarBilling
        return PolarBilling(store)
    return Billing(store)
