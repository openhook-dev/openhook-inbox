export async function renderAccount(main, {escapeHTML, copy, storageGet, storageSet}) {
  const view = main.querySelector('#account-view');
  async function request(path, data) {
    const response = await fetch(path, {method: data ? 'POST' : 'GET', credentials: 'same-origin',
      headers: {'Content-Type': 'application/json'}, ...(data ? {body: JSON.stringify(data)} : {})});
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'The request failed. Try again.');
    return result.data;
  }
  function openInbox(inbox) {
    const saved = storageGet('openhook-inboxes', []).filter(item => item.inbox_id !== inbox.inbox_id);
    if (!storageSet('openhook-inboxes', [{...inbox, name: inbox.name || 'Hosted inbox', hosted: true}, ...saved])) {
      throw new Error('Browser storage is unavailable. Enable it to open this inbox on this device.');
    }
    location.assign('/app');
  }
  async function load() {
    const data = await request('/api/account');
    if (!data.account) {
      view.innerHTML = '<section class="home-section"><h2>Keep your work connected.</h2><p>Use your GitHub identity for your hosted account. Sign-in does not request repository access.</p>' +
        (data.sign_in_available ? '<a class="button" href="/auth/github">Continue with GitHub</a>' : '<p>Hosted sign-in is not available yet. You can still <a href="/app">try a free inbox</a> or <a href="/connect">run Openhook yourself</a>.</p>') + '</section>';
      return;
    }
    const usage = data.usage;
    const paid = usage.plan === 'pro';
    const date = usage.paid_until ? new Date(usage.paid_until * 1000).toLocaleDateString() : '';
    const number = value => Number(value).toLocaleString();
    view.innerHTML = `<p id="account-status" role="status" aria-live="polite"></p>
      <section class="home-section"><h2>Signed in as ${escapeHTML(data.account.login)}</h2><button class="button" id="account-sign-out">Sign out on this device</button></section>
      <section class="home-section"><h2>${paid ? 'Pro' : 'Your hosted plan'}</h2>
      <p>${paid ? `Paid access through ${escapeHTML(date)}. Renewals keep your endpoint addresses.` : 'Pro keeps your inboxes connected across projects and devices.'}</p>
      <p>${data.billing_available ? '$19 USD per month, plus applicable tax. Renews monthly until canceled.' : 'Pro is being prepared for launch. Checkout is not available yet.'}</p>
      ${data.billing_available && !paid ? '<button class="button" data-billing="checkout">Continue to Pro checkout</button>' : ''}
      ${data.billing_management_available && data.billing_customer ? '<button class="button" data-billing="portal">Manage billing and cancellation</button>' : ''}
      <p>${number(usage.inboxes)} / ${number(usage.limits.inboxes)} inboxes · ${number(usage.events)} / ${number(usage.limits.monthly_events)} events in ${escapeHTML(usage.month)} (UTC).</p>
      <p>${number(Math.ceil(usage.retained_bytes / 1024 / 1024))} / 1,024 MiB stored. Payloads expire after 30 days. Limits stop new events; there are no automatic overage charges.</p>
      <button class="button" id="account-refresh">Refresh account</button></section>
      <section class="home-section"><h2>Your persistent inboxes</h2>
      ${data.inboxes.length ? data.inboxes.map(inbox => `<p>${escapeHTML(inbox.name || 'Hosted inbox')} · ${number(inbox.events)} events <button class="button small" data-inbox="${escapeHTML(inbox.id)}">Open inbox</button></p>`).join('') : '<p>No persistent inboxes yet. <a href="/app">Try a free temporary inbox</a> at any time.</p>'}
      ${paid ? '<form id="account-inbox-form"><label>Name your inbox<input name="name" maxlength="60" required placeholder="Payment integration" autocomplete="off"></label><button class="button" type="submit">Create persistent inbox</button></form>' : ''}
      <p>Opening an inbox saves its private access token on this device. After paid access ends, new events stop; inbox access remains available for up to 30 days, with the same payload retention limit.</p></section>
      <section class="home-section"><h2>Agent keys</h2><p>A key lets your agent create and recover your hosted inboxes. It cannot sign in to the browser or manage billing.</p>
      <div id="account-keys">${data.keys.length ? data.keys.map(key => `<p>${escapeHTML(key.name)} · …${escapeHTML(key.suffix)} <button class="button small" data-revoke="${escapeHTML(key.id)}">Revoke</button></p>`).join('') : '<p>No agent keys yet.</p>'}</div>
      <form id="account-key-form"><label>Name this key<input name="name" maxlength="60" required placeholder="My coding agent" autocomplete="off"></label><button class="button" type="submit">Create agent key</button></form>
      <div id="account-new-key" hidden></div>
      <p>Pass your key as <code>account_key</code> to <code>create_webhook</code> or <code>get_hosted_inboxes</code>. Keep it out of source control and shared conversations. <a href="/docs#get_hosted_inboxes">Tool reference</a>.</p>
      <p>Revoking an agent key stops account access. Previously issued inbox tokens remain valid until rotated or expired.</p></section>`;
    const status = view.querySelector('#account-status');
    if (new URLSearchParams(location.search).has('checkout')) {
      status.textContent = paid ? 'Payment confirmed. Your hosted plan is ready.' : 'Waiting for payment confirmation. Refresh your account shortly; returning from checkout does not confirm payment.';
    }
    function action(button, task) {
      button.disabled = true;
      status.textContent = '';
      return task().catch(error => { status.textContent = error.message; }).finally(() => { button.disabled = false; });
    }
    view.querySelector('#account-refresh').addEventListener('click', event => action(event.currentTarget, load));
    view.querySelector('#account-sign-out').addEventListener('click', event => action(event.currentTarget, async () => {
      await request('/api/account/sign-out', {});
      storageSet('openhook-inboxes', storageGet('openhook-inboxes', []).filter(inbox => !inbox.hosted));
      await load();
    }));
    view.querySelectorAll('[data-billing]').forEach(button => button.addEventListener('click', () => action(button, async () => {
      const result = await request('/api/account/billing/' + button.dataset.billing, {});
      location.assign(result.url);
    })));
    view.querySelectorAll('[data-inbox]').forEach(button => button.addEventListener('click', () => action(button, async () => {
      openInbox(await request('/api/account/inboxes/' + encodeURIComponent(button.dataset.inbox) + '/access', {}));
    })));
    view.querySelector('#account-inbox-form')?.addEventListener('submit', event => {
      event.preventDefault();
      const form = event.currentTarget;
      action(form.querySelector('button'), async () => openInbox(await request('/api/account/inboxes', {name: new FormData(form).get('name')})));
    });
    view.querySelectorAll('[data-revoke]').forEach(button => button.addEventListener('click', () => action(button, async () => {
      await request('/api/account/keys/' + encodeURIComponent(button.dataset.revoke) + '/revoke', {}); await load();
    })));
    view.querySelector('#account-key-form').addEventListener('submit', async event => {
      event.preventDefault();
      const form = event.currentTarget;
      await action(form.querySelector('button'), async () => {
        const result = await request('/api/account/keys', {name: new FormData(form).get('name')});
        await load();
        const output = view.querySelector('#account-new-key');
        output.hidden = false;
        output.innerHTML = `<h3>Save this key now</h3><p>It is shown once. Store it privately with your agent configuration.</p><div class="code-box"><pre>${escapeHTML(result.key)}</pre><button class="button">Copy key</button></div>`;
        output.querySelector('button').addEventListener('click', event => copy(result.key, event.currentTarget));
      });
    });
  }
  try { await load(); } catch (error) {
    view.replaceChildren();
    const message = document.createElement('p'); message.textContent = error.message; view.append(message);
    const retry = document.createElement('button'); retry.className = 'button'; retry.textContent = 'Try again';
    retry.addEventListener('click', () => renderAccount(main, {escapeHTML, copy, storageGet, storageSet})); view.append(retry);
  }
}
