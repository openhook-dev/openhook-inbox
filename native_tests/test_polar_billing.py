"""Signed Polar deliveries, canonical provider reads and durable failure cases."""
import asyncio
import base64
import json
import time
from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

import httpx
import pytest
import respx
from standardwebhooks import Webhook
from starlette.testclient import TestClient

from openhook.accounts import Accounts
from openhook.billing import billing_for
from openhook.errors import InboxError
from openhook.polar_billing import POLAR_VERSION, PolarBilling
from openhook.settings import Settings
from openhook.store import Store
from openhook.web import create_app

API = 'https://sandbox-api.polar.sh/v1/'
ORG, PRODUCT, PRICE, CUSTOMER, SUB, ORDER, CHECKOUT = [str(uuid4()) for _ in range(7)]
SECRET = 'whsec_' + base64.b64encode(b'polar-test-secret-with-32-bytes!!').decode()


@pytest.fixture
def billing(tmp_path):
    settings = Settings(database=str(tmp_path/'polar.db'), hosted_enabled=True, billing_enabled=True,
        billing_provider='polar', polar_access_token='test-token', polar_webhook_secret=SECRET,
        polar_organization_id=ORG, polar_product_id=PRODUCT, polar_price_id=PRICE)
    store = Store(settings)
    account, session = Accounts(store).sign_in(1, 'buyer')
    return PolarBilling(store), account['id'], session


def delivery(kind='order.paid', obj=ORDER, msg=None, when=None):
    body = json.dumps({'type':kind, 'data':{'id':obj}}).encode()
    when = when or datetime.now(timezone.utc)
    msg = msg or str(uuid4())
    return body, {'webhook-id':msg,'webhook-timestamp':str(int(when.timestamp())),
                  'webhook-signature':Webhook(SECRET).sign(msg, when, body.decode())}


def iso(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def order(account, **changes):
    now = int(time.time())
    value = {'id':ORDER,'product_id':PRODUCT,'customer':{'id':CUSTOMER,'external_id':account,'organization_id':ORG},
        'subscription_id':SUB,'metadata':{'openhook_account':account},'status':'paid','paid':True,
        'currency':'usd','net_amount':1900,'items':[{'product_price_id':PRICE,'proration':False,'amount':1900,
                                                 'start_timestamp':iso(now),'end_timestamp':iso(now+30*86400)}]}
    value.update(changes)
    return value


def mock_product(router):
    product = {'id':PRODUCT,'organization_id':ORG,'is_archived':False,'is_recurring':True,
               'recurring_interval':'month','recurring_interval_count':1,
               'prices':[{'id':PRICE,'amount_type':'fixed','price_currency':'usd','price_amount':1900,'is_archived':False}]}
    route = router.get(API+'products/'+PRODUCT).respond(200,json=product)
    router.get(API+'organizations/'+ORG).respond(200,json={'default_tax_behavior':'exclusive'})
    return route, product


def mock_checkout(router, account):
    mock_product(router)
    router.get(API+'customers/external/'+account).respond(404)
    value = {'id':CHECKOUT,'url':'https://sandbox.polar.sh/checkout/test','status':'open',
             'product_id':PRODUCT,'product_price_id':PRICE,'currency':'usd','tax_behavior':'exclusive'}
    return router.post(API+'checkouts/').respond(201,json=value), value


async def test_paid_renewal_replay_and_older_order(billing):
    service, account, _ = billing
    with respx.mock as router:
        first = order(account)
        route = router.get(API+'orders/'+ORDER).respond(200,json=first)
        body, headers = delivery()
        await service.receive(body,headers)
        assert route.calls.last.request.headers['Polar-Version'] == POLAR_VERSION
        paid_until = service.entitlement(account)['paid_until']
        inbox = service.store.create(account=account)
        assert await service.receive(body,headers) == {'duplicate':True}
        await service.receive(*delivery())
        assert service.entitlement(account)['paid_until'] == paid_until
        renewal_id = str(uuid4())
        renewal = order(account,id=renewal_id)
        renewal['items'][0]['end_timestamp'] = iso(paid_until+86400)
        router.get(API+'orders/'+renewal_id).respond(200,json=renewal)
        await service.receive(*delivery(obj=renewal_id))
        await service.receive(*delivery())
        assert service.entitlement(account)['paid_until'] == paid_until+86400
        with service.store.connection() as db:
            assert db.execute('SELECT count(*) FROM polar_orders').fetchone()[0] == 2
            assert db.execute('SELECT expires FROM inboxes WHERE id=?',(inbox['inbox_id'],)).fetchone()[0] == paid_until+31*86400


@pytest.mark.parametrize('change', ['zero','unpaid','wrong_owner','wrong_org','wrong_price','proration','no_period','long_period'])
async def test_invalid_orders_never_grant(billing, change):
    service,account,_=billing
    value=order(account)
    if change=='zero': value['net_amount']=0
    if change=='unpaid':value['paid']=False
    if change=='wrong_owner':value['metadata']['openhook_account']='other'
    if change=='wrong_org':value['customer']['organization_id']=str(uuid4())
    if change=='wrong_price':value['items'][0]['product_price_id']=str(uuid4())
    if change=='proration':value['items'][0]['proration']=True
    if change=='no_period':value['items'][0].pop('end_timestamp')
    if change=='long_period':value['items'][0]['end_timestamp']=iso(time.time()+365*86400)
    with respx.mock as router:
        router.get(API+'orders/'+ORDER).respond(200,json=value)
        with pytest.raises(InboxError):await service.receive(*delivery())
    assert service.entitlement(account).get('paid_until',0)==0


async def test_signature_tampering_expiry_and_nonpayment_events(billing):
    service,account,_=billing
    body,headers=delivery()
    for candidate in ({}, {**headers,'webhook-signature':'broken'}):
        with pytest.raises(InboxError):await service.receive(body,candidate)
    with pytest.raises(InboxError):await service.receive(body+b' ',headers)
    with pytest.raises(InboxError):await service.receive(*delivery(when=datetime.fromtimestamp(1,timezone.utc)))
    for kind in ('checkout.updated','subscription.active','subscription.canceled'):
        assert await service.receive(*delivery(kind))=={'ignored':True}
    assert service.entitlement(account).get('paid_until',0)==0


async def test_full_refund_stays_revoked_after_stale_paid_delivery(billing):
    service,account,_=billing
    with respx.mock as router:
        route=router.get(API+'orders/'+ORDER).respond(200,json=order(account,status='refunded'))
        await service.receive(*delivery('order.refunded'))
        route.respond(200,json=order(account))
        await service.receive(*delivery())
    assert service.entitlement(account)['paid_until']==0


async def test_partial_refund_keeps_paid_time(billing):
    service,account,_=billing
    with respx.mock as router:
        router.get(API+'orders/'+ORDER).respond(200,json=order(account,status='partially_refunded'))
        await service.receive(*delivery('order.refunded'))
    assert service.entitlement(account)['paid_until']>time.time()


async def test_revocation_before_order_is_terminal(billing):
    service,account,_=billing
    value=order(account)
    with respx.mock as router:
        router.get(API+'subscriptions/'+SUB).respond(200,json={'product_id':PRODUCT,'status':'canceled','ended_at':iso(time.time()),
            'customer':value['customer'],'metadata':value['metadata']})
        router.get(API+'orders/'+ORDER).respond(200,json=value)
        await service.receive(*delivery('subscription.revoked',SUB))
        await service.receive(*delivery())
    assert service.entitlement(account)['paid_until']==0


async def test_api_failure_does_not_acknowledge_delivery(billing):
    service,account,_=billing
    body,headers=delivery()
    with respx.mock as router:
        route=router.get(API+'orders/'+ORDER).respond(500,json={'secret':'must-not-leak'})
        with pytest.raises(InboxError,match='temporarily unavailable'):await service.receive(body,headers)
        route.respond(200,json=order(account))
        await service.receive(body,headers)
    assert service.entitlement(account)['paid_until']>time.time()


async def test_checkout_reuses_session_and_binds_server_identity(billing):
    service,account,_=billing
    with respx.mock as router:
        route,value=mock_checkout(router,account)
        router.get(API+'checkouts/'+CHECKOUT).respond(200,json=value)
        assert await service.checkout(account)==value['url']
        assert await service.checkout(account)==value['url']
        assert route.call_count==1
        payload=json.loads(route.calls.last.request.content)
        assert payload['external_customer_id']==account
        assert payload['metadata']['openhook_account']==account
        assert payload['allow_trial'] is False and payload['allow_discount_codes'] is False


async def test_checkout_concurrency_and_uncertain_failure_do_not_double_create(billing):
    service,account,_=billing
    with respx.mock as router:
        route,_=mock_checkout(router,account)
        route.respond(502)
        results=await asyncio.gather(service.checkout(account),service.checkout(account),return_exceptions=True)
        assert all(isinstance(result,InboxError) for result in results)
        assert route.call_count==1
        with pytest.raises(InboxError):await service.checkout(account)
        assert route.call_count==1


async def test_price_tax_and_duplicate_subscription_fail_closed(billing):
    service,account,_=billing
    with respx.mock as router:
        _,product=mock_product(router)
        router.get(API+'organizations/'+ORG).respond(200,json={'default_tax_behavior':'location'})
        with pytest.raises(InboxError):await service.checkout(account)
        mock_product(router)
        router.get(API+'customers/external/'+account).respond(200,json={'id':CUSTOMER,'organization_id':ORG,'external_id':account})
        router.get(API+'subscriptions/').respond(200,json={'items':[{'status':'past_due'}],'pagination':{'max_page':1}})
        with pytest.raises(InboxError,match='already exists'):await service.checkout(account)


async def test_portal_still_works_with_new_checkout_disabled(billing):
    service,account,_=billing
    service.store.settings=replace(service.settings,billing_enabled=False)
    service=PolarBilling(service.store)
    with respx.mock as router:
        router.get(API+'customers/external/'+account).respond(200,json={'id':CUSTOMER,'organization_id':ORG,'external_id':account})
        router.post(API+'customer-sessions/').respond(201,json={'customer_portal_url':'https://sandbox.polar.sh/openhook/portal'})
        assert await service.portal(account)=='https://sandbox.polar.sh/openhook/portal'
        with pytest.raises(InboxError):await service.checkout(account)


async def test_database_rejects_provider_and_environment_switch(billing):
    service,account,_=billing
    with respx.mock as router:
        router.get(API+'orders/'+ORDER).respond(200,json=order(account))
        await service.receive(*delivery())
    for settings in (replace(service.settings,polar_sandbox=False),replace(service.settings,billing_provider='stripe')):
        with pytest.raises(InboxError,match='separate database'):Store(settings)


def test_polar_route_and_factory_are_selected(billing):
    service,account,session=billing
    assert isinstance(billing_for(service.store),PolarBilling)
    with TestClient(create_app(service.settings)) as client:
        assert client.post('/billing/polar',content=b'{}').status_code==401
        assert client.post('/billing/stripe',content=b'{}').status_code==404
        assert client.post('/api/account/billing/checkout').status_code==403
        assert 'Polar processes' in client.get('/privacy').text
        assert 'test-token' not in repr(service.settings)
