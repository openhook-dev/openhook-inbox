import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {test} from 'node:test';
import assert from 'node:assert/strict';

function tracker(pathname = '/pricing', preferences = {}) {
  const context = {window: {}, navigator: preferences, URL,
    location: {pathname, hostname: 'openhook.dev', origin: 'https://openhook.dev', search: '?token=secret'},
    document: {title: 'Pricing', referrer: 'https://example.org/private?token=secret#secret', addEventListener() {}}};
  runInNewContext(readFileSync('web/assets/analytics.js', 'utf8'), context);
  return context.window.openhookAnalyticsBeforeSend;
}

test('only safe public page fields and approved event names leave the browser', () => {
  const clean = tracker()('event', {website: 'website-id', url: '/account?token=secret', name: 'pro-click',
    id: 'customer-id', data: {token: 'secret'}, referrer: '/private', language: 'en', screen: '100x100'});
  assert.equal(clean.url, '/pricing');
  assert.equal(clean.referrer, 'https://example.org');
  assert.equal(clean.name, 'pro-click');
  assert.equal(clean.data, undefined);
  assert.equal(clean.id, undefined);
  assert.ok(!JSON.stringify(clean).includes('secret'));
  assert.equal(tracker()('identify', {id: 'customer'}), false);
  assert.equal(tracker()('event', {name: 'arbitrary-secret'}), false);
});

test('private paths and privacy signals disable sending', () => {
  for (const path of ['/account', '/app', '/h/secret', '/auth/github/callback']) assert.equal(tracker(path)('event', {}), false);
  assert.equal(tracker('/', {doNotTrack: '1'})('event', {}), false);
  assert.equal(tracker('/', {globalPrivacyControl: true})('event', {}), false);
});


test('published guides and information pages are tracked without query data', () => {
  for (const path of ['/about', '/contact', '/guides', '/guides/callback-proof',
    '/guides/webhook-testing', '/guides/local-webhooks', '/guides/github-webhooks', '/guides/self-hosting']) {
    const clean = tracker(path)('event', {website: 'website-id', url: path + '?token=secret'});
    assert.equal(clean.url, path);
    assert.ok(!JSON.stringify(clean).includes('secret'));
    assert.equal(tracker(path, {doNotTrack: '1'})('event', {}), false);
    assert.equal(tracker(path, {globalPrivacyControl: true})('event', {}), false);
  }
  assert.equal(tracker('/guides/unknown-private-value')('event', {}), false);
});
