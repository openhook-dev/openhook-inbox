'use strict';

// Public pages only. Do not forward arbitrary event data, URLs, or DOM text.
// The server supplies its canonical public routes; unknown/private routes fail closed.
let analyticsPaths = new Set();
try { analyticsPaths = new Set(JSON.parse(document.currentScript?.dataset.publicPaths || '[]')); } catch {}
const analyticsEvents = new Set(['connect-click', 'channels-click', 'source-click', 'star-click', 'copy-setup-click']);
window.openhookAnalyticsBeforeSend = (type, payload) => {
  if (navigator.doNotTrack === '1' || navigator.globalPrivacyControl ||
      !analyticsPaths.has(location.pathname) || type !== 'event' ||
      (payload.name && !analyticsEvents.has(payload.name))) return false;
  let referrer = '';
  try {
    const url = new URL(document.referrer);
    if (url.protocol === 'https:' || url.protocol === 'http:') referrer = url.origin;
  } catch {}
  return {
    website: payload.website, hostname: location.hostname, url: location.pathname,
    title: document.title, language: payload.language, screen: payload.screen,
    referrer, ...(payload.name ? {name: payload.name} : {}),
  };
};

document.addEventListener('click', event => {
  if (!analyticsPaths.has(location.pathname)) return;
  const link = event.target.closest('a[href]');
  const button = event.target.closest('button.copy-code');
  const action = event.target.closest('[data-analytics-event]');
  let name = action?.dataset.analyticsEvent || (button ? 'copy-setup-click' : '');
  if (!name && link) {
    const url = new URL(link.href, location.origin);
    if (url.origin === location.origin) {
      name = {'/connect': 'connect-click', '/channels': 'channels-click'}[url.pathname] || '';
    } else if (url.origin === 'https://github.com' && url.pathname === '/openhook-dev/openhook-inbox') {
      name = 'source-click';
    }
  }
  if (analyticsEvents.has(name)) window.umami?.track(name);
});
