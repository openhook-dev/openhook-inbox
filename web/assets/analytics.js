'use strict';

// Public pages only. Do not forward arbitrary event data, URLs, or DOM text.
const analyticsPaths = new Set(['/', '/about', '/contact', '/connect', '/docs', '/agents', '/privacy']);
const analyticsEvents = new Set(['connect-click', 'channels-click', 'source-click', 'copy-setup-click']);
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
  const link = event.target.closest('a[href]');
  const button = event.target.closest('button.copy-code');
  let name = button ? 'copy-setup-click' : '';
  if (link) {
    const url = new URL(link.href, location.origin);
    if (url.origin === location.origin) {
      name = {'/connect': 'connect-click', '/channels': 'channels-click'}[url.pathname] || '';
    } else if (url.origin === 'https://github.com' && url.pathname === '/openhook-dev/openhook-inbox') {
      name = 'source-click';
    }
  }
  if (name) window.umami?.track(name);
});
