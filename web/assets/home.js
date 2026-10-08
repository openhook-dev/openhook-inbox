export function renderHome(main, { origin, copy, api, storageGet, storageSet }) {
  main.innerHTML = `
    <div class="text-home">
      <section class="intro" aria-labelledby="intro-title">
        <h1 id="intro-title">An inbox for your agent.</h1>
        <p>Create a webhook URL. Let your agent wait for the reply, then carry on.</p>
        <div class="actions"><a href="/app">Create an inbox</a><a href="/connect">Connect your agent</a></div>
        <p class="quiet">Open source. No account needed.</p>
      </section>
      <section class="home-section" aria-labelledby="connect-title">
        <h2 id="connect-title">Add Openhook to your agent.</h2>
        <pre id="quick-command"></pre>
        <button id="quick-connect" class="button">Copy command</button>
        <p class="quiet"><a href="/connect">Setup for Cursor, VS Code, and local clients</a></p>
      </section>
      <section class="home-section" aria-labelledby="flow-title">
        <h2 id="flow-title">A small loop.</h2>
        <ol class="plain-steps"><li>Create an inbox.</li><li>Give its URL to GitHub, Stripe, or another service.</li><li>Your agent reads the event and continues.</li></ol>
        <p>Receive emails too. Forward events to a local app or a running OpenClaw agent.</p>
        <p class="quiet"><a href="/docs">Read the tools</a></p>
      </section>
      <section class="home-section" aria-labelledby="try-title">
        <h2 id="try-title">Try a real webhook.</h2>
        <p>Create an inbox, send a request, and see what arrived.</p>
        <button id="send-callback" class="button">Send a webhook</button>
        <p id="callback-status" class="quiet" role="status" aria-live="polite"></p>
        <pre id="callback-body" hidden></pre>
        <button id="open-callback" class="button" hidden>Open this inbox</button>
      </section>
      <section class="home-section" aria-labelledby="host-title">
        <h2 id="host-title">Hosted here. Or by you.</h2>
        <p>Openhook receives and stores its own events. Use this service or run it on your server.</p>
        <p><a href="https://github.com/openhook-dev/openhook-inbox">Source on GitHub</a></p>
        <p class="quiet">Inboxes last up to seven days. Keep your reading key private.</p>
      </section>
    </div>`;
  const command = main.querySelector('#quick-command');
  command.textContent = 'claude mcp add --transport http openhook ' + origin + '/mcp';
  main.querySelector('#quick-connect').addEventListener('click', event => copy(command.textContent, event.currentTarget));
  const send = main.querySelector('#send-callback');
  const open = main.querySelector('#open-callback');
  const status = main.querySelector('#callback-status');
  const body = main.querySelector('#callback-body');
  let inbox;
  let sequence = 0;

  send.addEventListener('click', async () => {
    if (send.disabled) return;
    send.disabled = true;
    status.textContent = 'Sending…';
    try {
      inbox ||= await api('create');
      const response = await fetch(inbox.url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: 'landing.callback', sequence: sequence + 1 }),
      });
      if (!response.ok) {
        if (response.status === 404) { inbox = null; open.hidden = true; body.hidden = true; }
        throw new Error('The webhook did not arrive. Try again.');
      }
      const result = await api('get', { token: inbox.token, request_id: response.headers.get('x-openhook-event') });
      sequence++;
      status.textContent = 'Received. HTTP ' + response.status + '.';
      body.textContent = result.request.content;
      body.hidden = false;
      open.hidden = false;
    } catch (error) {
      status.textContent = error.message;
    } finally {
      send.disabled = false;
    }
  });
  open.addEventListener('click', () => {
    const saved = storageGet('openhook-inboxes', []);
    const bookmarks = Array.isArray(saved) ? saved : [];
    if (!bookmarks.some(item => item.token === inbox.token)) bookmarks.unshift({ ...inbox, name: 'Website demo' });
    if (storageSet('openhook-inboxes', bookmarks)) location.assign('/app');
    else status.textContent = 'Browser storage is unavailable. You can read the event here.';
  });
}
