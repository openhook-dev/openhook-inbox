import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {test} from 'node:test';
import assert from 'node:assert/strict';

const publicPaths = ['/', '/about', '/contact', '/connect', '/docs', '/agents', '/privacy',
  '/use-cases', '/use-cases/agent-to-agent-messaging', '/use-cases/team-handoffs', '/use-cases/agent-notifications'];

function browser(pathname = '/connect', preferences = {}, paths = JSON.stringify(publicPaths)) {
  const handlers = {};
  const events = [];
  const context = {window: {}, navigator: preferences, URL,
    location: {pathname, hostname: 'openhook.dev', origin: 'https://openhook.dev', search: '?token=secret'},
    document: {title: 'Connect', referrer: 'https://example.org/private?token=secret#secret',
      currentScript: {dataset: {publicPaths: paths}},
      addEventListener(name, handler) { handlers[name] = handler; }}};
  runInNewContext(readFileSync('web/assets/analytics.js', 'utf8'), context);
  context.window.umami = {track: name => events.push(name)};
  return {beforeSend: context.window.openhookAnalyticsBeforeSend, handlers, events};
}
const tracker = (...args) => browser(...args).beforeSend;

test('only safe public page fields and approved event names leave the browser', () => {
  const clean = tracker()('event', {website: 'website-id', url: '/account?token=secret', name: 'connect-click',
    id: 'customer-id', data: {token: 'secret'}, referrer: '/private', language: 'en', screen: '100x100'});
  assert.equal(clean.url, '/connect');
  assert.equal(clean.referrer, 'https://example.org');
  assert.equal(clean.name, 'connect-click');
  assert.equal(clean.data, undefined);
  assert.equal(clean.id, undefined);
  assert.ok(!JSON.stringify(clean).includes('secret'));
  assert.equal(tracker()('identify', {id: 'customer'}), false);
  assert.equal(tracker()('event', {name: 'arbitrary-secret'}), false);
});

test('private paths and privacy signals disable sending', () => {
  for (const path of ['/account', '/app', '/channels', '/sessions', '/h/secret', '/auth/github/callback']) assert.equal(tracker(path)('event', {}), false);
  assert.equal(tracker('/', {doNotTrack: '1'})('event', {}), false);
  assert.equal(tracker('/', {globalPrivacyControl: true})('event', {}), false);
});


test('public channel information pages are tracked without query data', () => {
  for (const path of publicPaths) {
    const clean = tracker(path)('event', {website: 'website-id', url: path + '?token=secret'});
    assert.equal(clean.url, path);
    assert.ok(!JSON.stringify(clean).includes('secret'));
    assert.equal(tracker(path, {doNotTrack: '1'})('event', {}), false);
    assert.equal(tracker(path, {globalPrivacyControl: true})('event', {}), false);
  }
  assert.equal(tracker('/guides/unknown-private-value')('event', {}), false);
});

test('missing or malformed public route configuration fails closed', () => {
  for (const paths of ['', 'not-json']) assert.equal(browser('/', {}, paths).beforeSend('event', {}), false);
});

test('React setup, in-page connect and star controls report only approved click names', () => {
  const page = browser('/');
  for (const name of ['copy-setup-click', 'connect-click', 'star-click', 'secret-unapproved-name']) {
    page.handlers.click({target: {closest: selector => selector === '[data-analytics-event]'
      ? {dataset: {analyticsEvent: name}} : null}});
  }
  assert.deepEqual(page.events, ['copy-setup-click', 'connect-click', 'star-click']);
  const privatePage = browser('/channels');
  privatePage.handlers.click({target: {closest: () => ({dataset: {analyticsEvent: 'star-click'}})}});
  assert.deepEqual(privatePage.events, []);
  assert.equal(tracker()('event', {name:'star-click',data:{token:'secret'}}).data, undefined);
});
