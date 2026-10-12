"""Polar hosted billing. Signed notifications trigger canonical API reads.

Only a positive paid order's own service period grants access. Subscription
state and browser returns never create paid time. Refunds and revocations are
terminal ledger entries, including when notifications arrive out of order.
"""

from datetime import datetime
import time
from urllib.parse import quote
from uuid import UUID, uuid4

import httpx
from standardwebhooks import Webhook, WebhookVerificationError

from openhook.billing import BillingBase
from openhook.errors import InboxError
from openhook.hosted_store import PRO_RETENTION_SECONDS

POLAR_VERSION = "2026-10"


def identifier(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise InboxError("Invalid billing identifier.", 400) from None


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError
        return parsed.timestamp()
    except (ValueError, TypeError, AttributeError, OverflowError):
        raise InboxError("Invalid billing period.", 400) from None


class PolarBilling(BillingBase):
    @property
    def hostname(self):
        return "sandbox.polar.sh" if self.settings.polar_sandbox else "polar.sh"

    async def api(self, method, path, data=None, *, allow_missing=False):
        self.require_configured()
        host = "sandbox-api.polar.sh" if self.settings.polar_sandbox else "api.polar.sh"
        try:
            async with httpx.AsyncClient(timeout=7, trust_env=False, follow_redirects=False) as client:
                response = await client.request(method, f"https://{host}/v1/{path}", json=data,
                    headers={"Authorization": "Bearer " + self.settings.polar_access_token,
                             "Polar-Version": POLAR_VERSION})
                if allow_missing and response.status_code == 404:
                    return None
                response.raise_for_status()
                result = response.json()
                if not isinstance(result, dict):
                    raise ValueError
                return result
        except (httpx.HTTPError, ValueError):
            raise InboxError("Billing is temporarily unavailable. Please retry shortly.", 502) from None

    async def validate_product(self):
        s = self.settings
        product = await self.api("GET", "products/" + quote(s.polar_product_id, safe=""))
        organization = await self.api("GET", "organizations/" + quote(s.polar_organization_id, safe=""))
        prices = [p for p in product.get("prices", []) if not p.get("is_archived")]
        if (product.get("id") != s.polar_product_id or product.get("organization_id") != s.polar_organization_id
                or product.get("is_archived") is not False or product.get("is_recurring") is not True
                or product.get("recurring_interval") != "month" or product.get("recurring_interval_count") != 1
                or product.get("trial_interval") is not None or len(prices) != 1):
            raise InboxError("The hosted product is not configured correctly.", 503)
        price = prices[0]
        tax = price.get("tax_behavior") or organization.get("default_tax_behavior")
        if (price.get("id") != s.polar_price_id or price.get("amount_type") != "fixed"
                or price.get("price_amount") != 1900 or price.get("price_currency") != "usd" or tax != "exclusive"):
            raise InboxError("The hosted price is not configured correctly.", 503)

    async def customer(self, account):
        customer = await self.api("GET", "customers/external/" + quote(account, safe=""), allow_missing=True)
        if customer is None:
            return None
        if customer.get("organization_id") != self.settings.polar_organization_id or customer.get("external_id") != account:
            raise InboxError("The billing customer does not match this account.", 409)
        customer_id = identifier(customer.get("id"))
        with self.store.connection(write=True) as db:
            db.execute("INSERT INTO hosted_entitlements(account,customer_id,updated) VALUES(?,?,?) "
                       "ON CONFLICT(account) DO UPDATE SET customer_id=excluded.customer_id,updated=excluded.updated",
                       (account, customer_id, time.time()))
        return customer_id

    async def checkout(self, account):
        self.require_available()
        if self.entitlement(account).get("paid_until", 0) > time.time():
            raise InboxError("You already have Pro. Use Manage billing for your subscription.", 409)
        await self.validate_product()
        customer = await self.customer(account)
        if customer:
            subscriptions = await self.api("GET", "subscriptions/?customer_id=" + customer + "&limit=100")
            items = subscriptions.get("items", [])
            if subscriptions.get("pagination", {}).get("max_page", 1) > 1 or any(
                    item.get("status") != "canceled" for item in items):
                raise InboxError("A subscription already exists. Use Manage billing or wait for payment confirmation.", 409)
        with self.store.connection() as db:
            row = db.execute("SELECT * FROM billing_attempts WHERE account=?", (account,)).fetchone()
            previous = dict(row) if row else None
        if previous and previous["session_id"]:
            session = await self.api("GET", "checkouts/" + quote(previous["session_id"], safe=""))
            if session.get("status") == "open":
                return self.redirect_url(session, self.hostname)
            if session.get("status") != "expired" and not (session.get("status") == "succeeded" and customer):
                raise InboxError("Payment is being confirmed. Refresh your account shortly.", 409)
            with self.store.connection(write=True) as db:
                db.execute("DELETE FROM billing_attempts WHERE account=? AND identifier=?", (account, previous["identifier"]))
        # Polar does not promise Stripe-style idempotency. Claim before POST and
        # leave ambiguous failures pending for reconciliation, never double-create.
        attempt = str(uuid4())
        with self.store.connection(write=True) as db:
            claimed = db.execute("INSERT INTO billing_attempts(account,identifier,created) VALUES(?,?,?) ON CONFLICT DO NOTHING",
                                 (account, attempt, int(time.time()))).rowcount
        if not claimed:
            raise InboxError("Checkout is being prepared. If this persists, contact support before trying again.", 409)
        session = await self.api("POST", "checkouts/", {
            "products": [self.settings.polar_product_id], "external_customer_id": account,
            "metadata": {"openhook_account": account, "openhook_attempt": attempt},
            "allow_discount_codes": False, "allow_trial": False, "require_billing_address": True,
            "success_url": self.settings.origin + "/account?checkout=complete",
            "return_url": self.settings.origin + "/account",
        })
        url = self.redirect_url(session, self.hostname)
        session_id = identifier(session.get("id"))
        if (session.get("product_id") != self.settings.polar_product_id
                or session.get("product_price_id") != self.settings.polar_price_id
                or session.get("currency") != "usd" or session.get("amount") != 1900
                # Polar resolves session tax after collecting the buyer's address.
                # validate_product already requires exclusive catalog taxation.
                or session.get("tax_behavior") not in {None, "exclusive"}):
            raise InboxError("Checkout does not match the hosted price. Contact support.", 502)
        with self.store.connection(write=True) as db:
            db.execute("UPDATE billing_attempts SET session_id=?,url=? WHERE account=? AND identifier=?",
                       (session_id, url, account, attempt))
        return url

    async def portal(self, account):
        self.require_configured()
        customer = await self.customer(account)
        if not customer:
            raise InboxError("There is no billing account to manage yet.", 404)
        result = await self.api("POST", "customer-sessions/", {"customer_id": customer,
                                "return_url": self.settings.origin + "/account"})
        return self.redirect_url({"url": result.get("customer_portal_url")}, self.hostname)

    def owner(self, customer, metadata):
        account = customer.get("external_id")
        if (customer.get("organization_id") != self.settings.polar_organization_id
                or not account or metadata.get("openhook_account") != account):
            raise InboxError("The payment does not match a hosted account.", 400)
        with self.store.connection() as db:
            exists = db.execute("SELECT 1 FROM accounts WHERE id=?", (account,)).fetchone()
        if not exists:
            raise InboxError("The payment account was not found.", 400)
        return account, identifier(customer.get("id"))

    def refresh_entitlement(self, db, account, customer, now):
        paid = db.execute("SELECT subscription_id,period_end FROM polar_orders WHERE account=? AND refunded=0 "
                          "AND subscription_id NOT IN (SELECT subscription_id FROM polar_revocations) "
                          "ORDER BY period_end DESC LIMIT 1", (account,)).fetchone()
        until = paid["period_end"] if paid else 0
        subscription = paid["subscription_id"] if paid else None
        db.execute("INSERT INTO hosted_entitlements(account,customer_id,subscription_id,paid_until,status,updated) VALUES(?,?,?,?,?,?) "
                   "ON CONFLICT(account) DO UPDATE SET customer_id=excluded.customer_id,subscription_id=excluded.subscription_id,"
                   "paid_until=excluded.paid_until,status=excluded.status,updated=excluded.updated",
                   (account, customer, subscription, until, "paid" if until > now else "free", now))
        # Keep the existing retention promise even if access is revoked immediately.
        db.execute("UPDATE inboxes SET expires=MAX(expires,?) WHERE id IN (SELECT inbox FROM hosted_inboxes WHERE account=?)",
                   (until + PRO_RETENTION_SECONDS, account))

    async def receive(self, body, headers):
        self.require_configured()
        try:
            event = Webhook(self.settings.polar_webhook_secret).verify(body, dict(headers))
        except (WebhookVerificationError, ValueError, UnicodeError):
            raise InboxError("Invalid or expired Polar signature.", 401) from None
        if not isinstance(event, dict) or not isinstance(event.get("data"), dict):
            raise InboxError("Invalid billing event.", 400)
        event_id = "polar:" + headers["webhook-id"]
        kind, obj = event.get("type"), event["data"]
        with self.store.connection() as db:
            if db.execute("SELECT 1 FROM billing_events WHERE id=?", (event_id,)).fetchone():
                return {"duplicate": True}
        if kind not in {"order.paid", "order.refunded", "subscription.revoked"}:
            return {"ignored": True}
        object_id = identifier(obj.get("id"))
        if kind == "subscription.revoked":
            subscription = await self.api("GET", "subscriptions/" + object_id)
            if subscription.get("product_id") != self.settings.polar_product_id:
                return {"ignored": True}
            if subscription.get("status") != "canceled" or not subscription.get("ended_at"):
                raise InboxError("Subscription revocation is not confirmed yet.", 503)
            account, customer = self.owner(subscription.get("customer") or {}, subscription.get("metadata") or {})
            with self.store.connection(write=True) as db:
                db.execute("INSERT INTO polar_revocations VALUES(?,?) ON CONFLICT DO NOTHING", (object_id, account))
                self.refresh_entitlement(db, account, customer, time.time())
                db.execute("INSERT INTO billing_events VALUES(?,?,?) ON CONFLICT DO NOTHING", (event_id, kind, time.time()))
            return {"applied": True}
        order = await self.api("GET", "orders/" + object_id)
        if order.get("product_id") != self.settings.polar_product_id:
            return {"ignored": True}
        account, customer = self.owner(order.get("customer") or {}, order.get("metadata") or {})
        subscription = identifier(order.get("subscription_id"))
        matching = [item for item in order.get("items", []) if item.get("product_price_id") == self.settings.polar_price_id
                    and item.get("proration") is False and item.get("amount", 0) > 0]
        refunded = order.get("status") == "refunded"
        if (order.get("id") != object_id or order.get("currency") != "usd" or order.get("net_amount", 0) <= 0
                or len(matching) != 1 or (not refunded and (order.get("paid") is not True
                or order.get("status") not in {"paid", "partially_refunded"}))):
            raise InboxError("The order does not contain a paid hosted period.", 400)
        start, end = timestamp(matching[0].get("start_timestamp")), timestamp(matching[0].get("end_timestamp"))
        if not 0 < end - start <= 32 * 86400 or start > time.time() + 300:
            raise InboxError("Invalid paid service period.", 400)
        with self.store.connection(write=True) as db:
            if db.execute("SELECT 1 FROM billing_events WHERE id=?", (event_id,)).fetchone():
                return {"duplicate": True}
            db.execute("INSERT INTO polar_orders VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
                       "refunded=MAX(refunded,excluded.refunded),updated=excluded.updated",
                       (object_id, account, subscription, end, order["net_amount"], int(refunded), time.time()))
            self.refresh_entitlement(db, account, customer, time.time())
            db.execute("INSERT INTO billing_events VALUES(?,?,?)", (event_id, kind, time.time()))
        return {"applied": True}
