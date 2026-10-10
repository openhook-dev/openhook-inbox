export function renderHome(main, { origin, copy, api, storageGet, storageSet }) {
  const command = main.querySelector('#quick-command');
  command.textContent = 'claude mcp add --transport http openhook ' + origin + '/mcp';
  main.querySelector('#quick-connect').hidden = false;
  main.querySelector('#quick-connect').addEventListener('click', event => copy(command.textContent, event.currentTarget));
  const send = main.querySelector('#send-callback');
  const open = main.querySelector('#open-callback');
  const status = main.querySelector('#callback-status');
  const body = main.querySelector('#callback-body');
  send.hidden = false;
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
        credentials: 'omit',
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
