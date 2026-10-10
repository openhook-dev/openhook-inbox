"""Payment boundary tests use signed fixtures and mocked Stripe HTTP, never charges."""

import hashlib
import hmac
import json
import sqlite3
import time
from dataclasses import replace

import httpx
import pytest
import respx
from starlette.testclient import TestClient

from openhook.accounts import Accounts
from openhook.billing import Billing, STRIPE_VERSION
from openhook.settings import Settings
from openhook.store import InboxError, Store
from openhook.web import create_app

API = 'https://api.stripe.com/v1/'


@pytest.fixture
def billing(tmp_path):
    settings = Settings(database=str(tmp_path/'billing.sqlite3'), hosted_enabled=True, billing_enabled=True,
                        stripe_secret_key='sk_test_private', stripe_webhook_secret='whsec_private', stripe_price_id='price_pro')
    store = Store(settings)
    account, session = Accounts(store).sign_in(1, 'buyer')
    return Billing(store), account['id'], session


def sign(body, timestamp=None):
    sent = str(int(time.time()) if timestamp is None else timestamp)
    digest = hmac.new(b'whsec_private', sent.encode()+b'.'+body, hashlib.sha256).hexdigest()
    return 't='+sent+',v1='+digest


def event(invoice='in_one', identifier='evt_one', kind='invoice.paid', live=False):
    return json.dumps({'id':identifier,'type':kind,'livemode':live,'data':{'object':{'id':invoice}}}).encode()


def customer(billing, account):
    with billing.store.connection() as db:
        db.execute("INSERT INTO hosted_entitlements(account,customer_id,status,updated) VALUES(?,'cus_one','free',?)", (account,time.time()))


def payment_mocks(router, account, invoice='in_one', period=None, amount=1900, price='price_pro', owner=None):
    period = period or int(time.time())+30*86400
    router.get(API+'invoices/'+invoice).mock(return_value=httpx.Response(200,json={
        'id':invoice,'customer':'cus_one','parent':{'subscription_details':{'subscription':'sub_one'}},
        'status':'paid','amount_paid':amount,'currency':'usd','livemode':False}))
    router.get(API+'subscriptions/sub_one').mock(return_value=httpx.Response(200,json={
        'id':'sub_one','customer':'cus_one','metadata':{'openhook_account':owner or account},'livemode':False}))
    router.get(API+'invoices/'+invoice+'/lines?limit=100').mock(return_value=httpx.Response(200,json={
        'has_more':False,'data':[{'amount':1900,'period':{'end':period},'pricing':{'price_details':{'price':price}},
        'parent':{'subscription_item_details':{'subscription':'sub_one','proration':False}}}]}))
    return period


@pytest.mark.asyncio
async def test_only_verified_paid_invoice_grants_once_and_renewal_extends_inboxes(billing):
    service,account,_=billing
    customer(service,account)
    with respx.mock as router:
        paid_until=payment_mocks(router,account)
        body=event()
        assert await service.receive(body,sign(body))=={'applied':True}
        assert service.entitlement(account)['paid_until']==paid_until
        inbox=service.store.create(account=account)
        assert await service.receive(body,sign(body))=={'duplicate':True}
        same_invoice=event(identifier='evt_same_invoice')
        assert await service.receive(same_invoice,sign(same_invoice))=={'applied':False}
        renewed=payment_mocks(router,account,invoice='in_renewal',period=paid_until+30*86400)
        body=event(invoice='in_renewal',identifier='evt_renewal')
        await service.receive(body,sign(body))
        with service.store.connection() as db:
            assert db.execute('SELECT expires FROM inboxes WHERE id=?',(inbox['inbox_id'],)).fetchone()[0]==renewed+30*86400
            assert db.execute('SELECT COUNT(*) FROM paid_invoices').fetchone()[0]==2
        # Late delivery of an older, distinct invoice cannot shorten access.
        payment_mocks(router,account,invoice='in_old',period=paid_until-86400)
        body=event(invoice='in_old',identifier='evt_old')
        await service.receive(body,sign(body))
        assert service.entitlement(account)['paid_until']==renewed


@pytest.mark.asyncio
async def test_signature_mode_price_and_owner_fail_closed(billing):
    service,account,_=billing
    customer(service,account)
    body=event()
    for signature in ('',sign(body,1),sign(body)+'0'):
        with pytest.raises(InboxError):await service.receive(body,signature)
    with pytest.raises(InboxError):await service.receive(body+b' ',sign(body))
    live=event(live=True)
    with pytest.raises(InboxError):await service.receive(live,sign(live))
    with respx.mock as router:
        for kwargs in ({'price':'price_unrelated'},{'owner':'someone_else'},{'amount':0}):
            payment_mocks(router,account,**kwargs)
            with pytest.raises(InboxError):await service.receive(body,sign(body))
    assert service.entitlement(account)['paid_until']==0
    with service.store.connection() as db:
        assert db.execute('SELECT COUNT(*) FROM billing_events').fetchone()[0]==0


@pytest.mark.asyncio
async def test_checkout_return_failed_payment_and_cancellation_do_not_grant_time(billing):
    service,account,_=billing
    customer(service,account)
    for kind in ('checkout.session.completed','invoice.payment_failed','customer.subscription.deleted'):
        body=event(kind=kind)
        assert await service.receive(body,sign(body))=={'ignored':True}
    assert service.entitlement(account)['paid_until']==0


@pytest.mark.asyncio
async def test_provider_failure_and_transaction_failure_remain_retryable(billing):
    service,account,_=billing
    customer(service,account)
    body=event()
    with respx.mock as router:
        router.get(API+'invoices/in_one').mock(return_value=httpx.Response(503,text='private provider details'))
        with pytest.raises(InboxError,match='temporarily'):await service.receive(body,sign(body))
        payment_mocks(router,account)
        with service.store.connection() as db:
            db.execute("CREATE TRIGGER fail_billing BEFORE INSERT ON billing_events BEGIN SELECT RAISE(ABORT,'failed'); END")
        with pytest.raises(sqlite3.IntegrityError):await service.receive(body,sign(body))
        assert service.entitlement(account)['paid_until']==0
        with service.store.connection() as db:
            assert db.execute('SELECT COUNT(*) FROM paid_invoices').fetchone()[0]==0
            db.execute('DROP TRIGGER fail_billing')
        assert await service.receive(body,sign(body))=={'applied':True}


def pro_price():
    return {
        'active':True,'livemode':False,'unit_amount':1900,'currency':'usd','billing_scheme':'per_unit',
        'tax_behavior':'exclusive','transform_quantity':None,
        'recurring':{'interval':'month','interval_count':1,'usage_type':'licensed'}}


def checkout_mocks(router):
    router.get(API+'prices/price_pro').mock(return_value=httpx.Response(200,json=pro_price()))
    router.post(API+'customers').mock(return_value=httpx.Response(200,json={'id':'cus_one'}))
    router.get(API+'subscriptions?customer=cus_one&status=all&limit=100').mock(return_value=httpx.Response(200,json={'data':[],'has_more':False}))
    return router.post(API+'checkout/sessions').mock(return_value=httpx.Response(200,json={'id':'cs_one','url':'https://checkout.stripe.com/c/pay/test'}))


@pytest.mark.asyncio
@pytest.mark.parametrize('invalid', [
    {'recurring': None},
    {'recurring': {'interval':'month','interval_count':1,'usage_type':'metered'}},
    {'tax_behavior':'inclusive'},
    {'tax_behavior':'unspecified'},
    {'billing_scheme':'tiered'},
    {'transform_quantity':{'divide_by':10,'round':'up'}},
])
async def test_checkout_rejects_incompatible_prices_before_creating_customer(billing, invalid):
    service,account,_=billing
    price = pro_price()
    price.update(invalid)
    with respx.mock as router:
        router.get(API+'prices/price_pro').mock(return_value=httpx.Response(200,json=price))
        with pytest.raises(InboxError, match='price is not configured') as error:
            await service.checkout(account)
        assert error.value.status == 503
        assert len(router.calls) == 1
    assert service.entitlement(account) == {}


@pytest.mark.asyncio
async def test_checkout_is_stable_across_retries_and_cannot_double_subscribe(billing):
    service,account,_=billing
    with respx.mock as router:
        create=checkout_mocks(router)
        create.mock(return_value=httpx.Response(503))
        with pytest.raises(InboxError):await service.checkout(account)
        first=create.calls.last.request
        create.mock(return_value=httpx.Response(200,json={'id':'cs_one','url':'https://checkout.stripe.com/c/pay/test'}))
        assert await service.checkout(account)=='https://checkout.stripe.com/c/pay/test'
        second=create.calls.last.request
        assert first.headers['idempotency-key']==second.headers['idempotency-key']
        assert first.content==second.content
        assert second.headers['stripe-version']==STRIPE_VERSION
        assert b'price_pro' in second.content and b'automatic_tax' in second.content
        router.get(API+'checkout/sessions/cs_one').mock(return_value=httpx.Response(200,json={'status':'open','url':'https://checkout.stripe.com/c/pay/test'}))
        await service.checkout(account)
        assert create.call_count==2
        router.get(API+'subscriptions?customer=cus_one&status=all&limit=100').mock(return_value=httpx.Response(200,json={'data':[{'status':'past_due'}]}))
        with pytest.raises(InboxError,match='already exists'):await service.checkout(account)
    assert service.entitlement(account)['paid_until']==0


def test_billing_routes_require_browser_identity_and_webhook_signature(billing):
    service,account,session=billing
    key=Accounts(service.store).create_key(account,'agent')['key']
    with TestClient(create_app(service.settings),base_url=service.settings.origin) as client:
        assert client.post('/api/account/billing/checkout',headers={'authorization':'Bearer '+key,'origin':service.settings.origin}).status_code==401
        client.cookies.set('openhook-session',session)
        assert client.post('/api/account/billing/checkout').status_code==403
        assert client.get('/account?checkout=complete').status_code==200
        assert service.entitlement(account)=={}
        assert client.post('/billing/stripe',content=event()).status_code==401
        with respx.mock as router:
            checkout_mocks(router)
            response=client.post('/api/account/billing/checkout',headers={'origin':service.settings.origin},json={'price':'price_fake','customer':'cus_other'})
            assert response.status_code==200
            assert 'no-store' in response.headers['cache-control']
            router.post(API+'billing_portal/sessions').mock(return_value=httpx.Response(200,json={'url':'https://billing.stripe.com/p/session/test'}))
            portal=client.post('/api/account/billing/portal',headers={'origin':service.settings.origin})
            assert portal.status_code==200
            assert b'cus_one' in router.calls.last.request.content
    disabled=replace(service.settings,billing_enabled=False)
    with TestClient(create_app(disabled),base_url=disabled.origin) as client:
        client.cookies.set('openhook-session',session)
        assert client.post('/api/account/billing/checkout',headers={'origin':disabled.origin}).status_code==503


@pytest.mark.asyncio
async def test_verified_test_payments_cannot_be_promoted_to_live(billing):
    service,account,_=billing
    customer(service,account)
    with respx.mock as router:
        payment_mocks(router,account)
        body=event()
        await service.receive(body,sign(body))
    with pytest.raises(InboxError,match='separate database'):
        Store(replace(service.settings,stripe_live=True))
    assert service.entitlement(account)['paid_until']>time.time()


@pytest.mark.asyncio
async def test_expired_checkout_can_restart_but_unknown_completed_session_cannot(billing):
    service,account,_=billing
    with respx.mock as router:
        create=checkout_mocks(router)
        await service.checkout(account)
        old_key=create.calls.last.request.headers['idempotency-key']
        status=router.get(API+'checkout/sessions/cs_one').mock(return_value=httpx.Response(200,json={'status':'complete','subscription':'sub_unknown'}))
        with pytest.raises(InboxError,match='being confirmed'):await service.checkout(account)
        assert create.call_count==1
        status.mock(return_value=httpx.Response(200,json={'status':'expired'}))
        await service.checkout(account)
        assert create.calls.last.request.headers['idempotency-key']!=old_key
        assert create.call_count==2


@pytest.mark.asyncio
async def test_pausing_sales_preserves_renewals_and_customer_portal(billing):
    service,account,_=billing
    customer(service,account)
    paused=Billing(Store(replace(service.settings,billing_enabled=False)))
    assert not paused.available and paused.configured
    with pytest.raises(InboxError):await paused.checkout(account)
    with respx.mock as router:
        payment_mocks(router,account)
        body=event()
        assert await paused.receive(body,sign(body))=={'applied':True}
        router.post(API+'billing_portal/sessions').mock(return_value=httpx.Response(200,json={'url':'https://billing.stripe.com/p/session/test'}))
        assert await paused.portal(account)=='https://billing.stripe.com/p/session/test'
