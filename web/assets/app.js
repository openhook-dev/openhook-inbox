'use strict';

const main = document.querySelector('#main');
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const escapeHTML = (value = '') => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const origin = location.origin;
const icons = {
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
  moon: '<path d="M20.5 14A9 9 0 0 1 10 3a9 9 0 1 0 10.5 11Z"/>',
  inbox: '<path d="M4 4h16v16H4zM4 13h5l2 3h2l2-3h5"/>',
  email: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
  signal: '<path d="M4 12h3l3-7 4 14 3-7h3"/>',
};
const icon = (name, cls = 'feature-icon') => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${icons[name]}</svg>`;
const announce = text => { $('#announcement').textContent = text; };
function storageGet(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }
function storageSet(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { announce('Browser storage is unavailable. Copy your inbox URL before leaving.'); } }
function updateThemeButton() {
  const isDark = document.documentElement.dataset.theme === 'dark';
  $('#theme-toggle').innerHTML = icon(isDark ? 'sun' : 'moon', '');
  $('#theme-toggle').setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} theme`);
}
$('#theme-toggle').addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem('openhook-theme', next); } catch {}
  updateThemeButton();
});
updateThemeButton();

async function copy(text, button) {
  const original = button.textContent;
  try {
    await navigator.clipboard.writeText(text);
    button.textContent = 'Copied';
    announce('Copied to clipboard.');
    setTimeout(() => { if (button.isConnected) button.textContent = original; }, 1500);
  } catch {
    button.textContent = 'Select text';
    announce('Clipboard access is unavailable. Select and copy the text.');
  }
}

async function api(action, args = {}, signal) {
  const response = await fetch('/api/call', {method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({action, ...args}), signal});
  const result = await response.json();
  if (!response.ok || !result.success) throw new Error(result.message || 'The request could not be completed. Try again.');
  return result.data;
}

function homePage() {
  main.innerHTML = `
    <section class="hero">
      <div class="hero-copy"><div class="eyebrow"><span class="dot"></span> An inbox for your agent</div>
        <h1>The world sends events.<br>Your agent gets them.</h1>
        <p>Create a webhook, catch an email, wait for a callback. Give your agent a place to listen, then let it get back to work.</p>
        <div class="actions"><a class="button primary" href="/connect">Connect your agent <span aria-hidden="true">↗</span></a><a class="button" href="/app">Try an inbox <span aria-hidden="true">→</span></a></div>
        <span class="hero-note">Open source · 26 MCP tools · Self-hosted</span>
      </div>
      <div class="terminal" aria-label="Example agent workflow"><div class="terminal-bar"><span>agent / callback</span><span>Example</span></div><div class="terminal-body">
        <div class="terminal-step"><div class="terminal-prompt">› Create an inbox for this callback.</div><div class="terminal-response">create_webhook()</div><div class="terminal-response">↳ HTTP · email · DNS</div></div>
        <div class="terminal-step"><div class="terminal-prompt">› Wait for the event.</div><div class="terminal-response">wait_for_request(token, timeout=60)</div></div>
        <div class="terminal-step"><div class="terminal-result"><span class="dot"></span> Event received</div><div class="terminal-response">{"status": "complete", "id": "run_42"}</div></div>
      </div><div class="terminal-caption">create → listen → inspect → continue</div></div>
    </section>
    <div class="strip"><span>HTTP requests</span><span>Temporary email</span><span>DNS callbacks</span><span>Stdio + Streamable HTTP</span></div>
    <section class="section"><div class="section-heading"><span class="section-number">01</span><h2>One inbox. Three ways in.</h2></div>
      <div class="feature-grid"><article class="feature">${icon('inbox')}<h3>Receive a webhook</h3><p>Get a public URL in one call. Capture callbacks, inspect headers and bodies, and choose the response.</p></article><article class="feature">${icon('email')}<h3>Catch an email</h3><p>A temporary inbox for verification emails and test flows. Extract links and codes through MCP.</p></article><article class="feature">${icon('signal')}<h3>See a DNS callback</h3><p>Receive DNS lookups alongside HTTP and email events. Inspect out-of-band callbacks in systems you own.</p></article></div>
    </section>
    <section class="section"><div class="section-heading"><span class="section-number">02</span><h2>A small loop, done all the way.</h2></div>
      <div><div class="how-row"><h3>01 / Create</h3><p>Ask your agent for an inbox. It gets a URL, email address, and DNS name. Anonymous inboxes need no account.</p></div><div class="how-row"><h3>02 / Listen</h3><p>Give the address to the service sending the event. Wait through MCP or watch the live inspector in your browser.</p></div><div class="how-row"><h3>03 / Continue</h3><p>The waiting tool returns the captured event. Your running agent can inspect it and take the next step.</p></div></div>
      <p class="hero-note">Register GitHub, Stripe, or Linear subscriptions through MCP. Forward events to a local server or wake OpenClaw with the Openhook listener.</p>
    </section>
    <section class="section section-cta"><div><h2>Give your next task an inbox.</h2><p>No local HTTP server needed. Start in your browser or your MCP client.</p></div><a class="button primary" href="/app">Create an inbox <span aria-hidden="true">→</span></a></section>`;
}

const setups = {
  claude: {name:'Claude Code', title:'Connect from your terminal', code:`claude mcp add --transport http openhook ${origin}/mcp`, next:'Run the command, restart your session if needed, then ask Claude to create a webhook and wait for a test event.'},
  cursor: {name:'Cursor', title:'Add Openhook to your MCP configuration', code:JSON.stringify({mcpServers:{openhook:{url:`${origin}/mcp`}}}, null, 2), next:'Add this entry to .cursor/mcp.json or your MCP settings, then enable Openhook in the tools list.'},
  vscode: {name:'VS Code', title:'Add a workspace MCP server', code:JSON.stringify({servers:{openhook:{type:'http',url:`${origin}/mcp`}}},null,2), next:'Save this configuration in .vscode/mcp.json. Start Openhook from the MCP server list.'},
  local: {name:'Local / stdio', title:'Run the open-source server locally', code:'git clone https://github.com/openhook-dev/openhook-inbox.git\ncd openhook-inbox\nuv sync\nuv run openhook', next:'For a stdio client, use command "uv", args ["--directory", "/absolute/path/to/openhook", "run", "openhook"]. Keep the absolute path specific to your checkout.'},
};

function connectPage() {
  main.innerHTML = `<div class="page-head"><div><div class="eyebrow">Setup</div><h1>Connect your agent</h1><p>Choose your client. Create your first inbox in the next tool call.</p></div></div><div class="page-body"><div class="setup-grid"><div class="tabs" role="tablist" aria-label="MCP client" aria-orientation="vertical">${Object.entries(setups).map(([key,value],i)=>`<button class="tab" role="tab" id="tab-${key}" aria-controls="setup-panel" aria-selected="${i===0}" tabindex="${i===0?0:-1}" data-client="${key}">${value.name}</button>`).join('')}</div><div id="setup-panel" class="setup-content" role="tabpanel" aria-labelledby="tab-claude" tabindex="0"></div></div></div>`;
  function select(key) {
    const setup = setups[key];
    $$('.tab').forEach(tab => { const selected = tab.dataset.client===key; tab.setAttribute('aria-selected',selected); tab.tabIndex=selected?0:-1; });
    $('#setup-panel').setAttribute('aria-labelledby',`tab-${key}`);
    $('#setup-panel').innerHTML = `<div class="setup-step"><span class="step-number">1</span><h2>${setup.title}</h2></div><div class="code-box"><pre>${escapeHTML(setup.code)}</pre><button class="button small copy-code">Copy</button></div><p>${escapeHTML(setup.next)}</p><div class="setup-step"><span class="step-number">2</span><h2>Try the whole loop</h2></div><div class="code-box"><pre>Create a webhook inbox. Give me its HTTP URL.\nWait for the next request and show me its JSON body.</pre><button class="button small copy-code">Copy</button></div><p>Send a request to the URL from another terminal, or import the inbox into the <a class="inline-link" href="/app">browser inspector</a>.</p><div class="callout"><strong>Hosted or local?</strong> Openhook runs its own capture service and durable storage. Connect to this deployment or run your own. No external webhook account is needed.</div><a class="inline-link" href="/docs">Read the tool reference →</a>`;
    $$('.copy-code').forEach(button=>button.addEventListener('click',()=>copy(button.previousElementSibling.textContent,button)));
  }
  $$('.tab').forEach((tab,i)=>{
    tab.addEventListener('click',()=>select(tab.dataset.client));
    tab.addEventListener('keydown',event=>{const tabs=$$('.tab');let next;if(['ArrowDown','ArrowRight'].includes(event.key))next=(i+1)%tabs.length;if(['ArrowUp','ArrowLeft'].includes(event.key))next=(i-1+tabs.length)%tabs.length;if(event.key==='Home')next=0;if(event.key==='End')next=tabs.length-1;if(next!==undefined){event.preventDefault();tabs[next].focus();select(tabs[next].dataset.client);}});
  });
  select('claude');
}

async function docsPage() {
  main.innerHTML = `<div class="page-head"><div><div class="eyebrow">Documentation</div><h1>Small tools. A complete loop.</h1><p>26 native tools for HTTP, email, DNS, and event delivery.</p></div><a class="button small" href="/connect">Connect your agent →</a></div><div class="page-body"><div class="reading"><section><h2>Start with an inbox</h2><p><code>create_webhook</code> returns a token, HTTP URL, email address, and DNS name. Supply the address to the external service, then call <code>wait_for_request</code> or <code>wait_for_email</code>. Wait calls last up to 120 seconds and return to your running agent when an event arrives.</p><h3>Keep the token</h3><p>The private management token grants access to an inbox. Public capture addresses cannot read events. Store it with your task, keep it private, and use it to inspect events after reconnecting. The browser stores your inbox list on this device only.</p><h3>What is included</h3><p>A browser inspector, a hosted MCP endpoint, and 26 native tools. Openhook captures and stores its own events. Email and DNS addresses are returned when their listeners are configured.</p><h3>Retention and limits</h3><p>Inboxes expire within seven days and retain the latest 1000 events, each at most 1 MB. Use <code>server_status</code> to inspect enabled transports. Pass <code>next_since</code> when reconnecting a waiting agent to receive retained events after its last cursor.</p><h3>Registration and local forwarding</h3><p>Use register_github_webhook, register_stripe_webhook, or register_linear_webhook with your provider credentials. Credentials are used for the API call and are never saved. Unregister subscriptions before their inbox expires. Run openhook-listen --forward http://localhost:8080/webhook for local delivery, or openhook-listen --openclaw to wake a configured local agent. Set OPENHOOK_TOKEN to the private inbox token. The listener makes outbound HTTPS requests and resumes from its saved cursor.</p></section></div><div><h2>Tool reference</h2><p class="hero-note">Loaded from the running server so names and schemas stay current.</p></div><label class="tool-search">Search tools<input id="tool-search" type="search" placeholder="Search by name or purpose" autocomplete="off"></label><div id="tool-list" class="tool-list" aria-live="polite"><div class="skeleton long"></div><div class="skeleton short"></div></div><div class="reading"><section id="source"><h2>Open source</h2><p>Openhook is MIT-licensed. Run it locally, inspect the code, or contribute a new workflow.</p><h3>Run it yourself</h3><p><a class="inline-link" href="https://github.com/openhook-dev/openhook-inbox" target="_blank" rel="noopener noreferrer">Read the source on GitHub ↗</a>. Run <code>uv run openhook</code> for stdio, or <code>uv run openhook --http</code> to serve the website and MCP endpoint locally.</p></section></div></div>`;
  async function loadTools() {
    try {
      const response=await fetch('/api/tools');if(!response.ok)throw new Error('Could not load tools.');
      const {tools}=await response.json();
      function filter(){const query=$('#tool-search').value.toLowerCase();const filtered=tools.filter(t=>`${t.name} ${t.description}`.toLowerCase().includes(query));$('#tool-list').innerHTML=filtered.length?filtered.map(tool=>`<article class="tool-row"><div><code>${escapeHTML(tool.name)}</code><div class="tool-hint">${tool.annotations?.readOnlyHint?'Read only':tool.annotations?.destructiveHint?'Can change or delete data':'Creates or updates data'}</div></div><div><p>${escapeHTML(tool.description.split('\n')[0])}</p><details><summary class="hero-note">Parameters</summary><pre>${escapeHTML(JSON.stringify(tool.inputSchema,null,2))}</pre></details></div></article>`).join(''):'<div class="list-empty">No tools match. Try another search.</div>';}
      $('#tool-search').addEventListener('input',filter);filter();
    } catch {$('#tool-list').innerHTML='<div class="tool-error"><p>Could not load the tool reference. Check your connection and try again.</p><button class="button small" id="retry-tools">Try again</button></div>';$('#retry-tools').addEventListener('click',loadTools);}
  }
  await loadTools();
  if(location.hash)document.getElementById(location.hash.slice(1))?.scrollIntoView();
}

function privacyPage() {
  main.innerHTML='<div class="page-head"><div><div class="eyebrow">Privacy</div><h1>Know where your events go.</h1><p>Captured and stored by Openhook.</p></div></div><div class="page-body reading"><section><h2>Captured events</h2><p>Openhook stores incoming bodies, headers, sender addresses, timestamps, and notes in its database on its hosting server. Inboxes expire within seven days; periodic cleanup deletes expired inboxes and their events. Each inbox retains its latest 1000 events.</p></section><section><h2>On your device</h2><p>Your theme preference, inbox bookmarks, and private management tokens are saved in browser local storage. Bookmarks are not synchronized. Removing a bookmark leaves the inbox and its server events intact.</p></section><section><h2>Private tokens</h2><p>Anyone with an inbox management token can inspect or delete its events. Public capture addresses only accept events. The server stores hashes of management tokens. Provider API credentials are used only during registration and removal calls and are not saved. Optional signing secrets are stored with inbox settings to verify incoming webhook signatures. You can rotate tokens or permanently delete inboxes through MCP.</p></section><section><h2>Operational data</h2><p>HTTP rate-limit counters are held in memory. Application HTTP access logging is disabled; hosting and network providers may maintain operational logs. There are no advertising trackers or analytics scripts in the application.</p></section></div>';
}

function inboxPage() {
  let inboxes=storageGet('openhook-inboxes',[]).filter(item=>item&&typeof item.token==='string'&&item.token.startsWith('ohk_'));
  let active=inboxes[0]||null;
  let events=[];
  let selected=null;
  let page=1;
  let isLast=true;
  let polling=true;
  let listLoading=false;
  let controller=null;
  let detailController=null;
  let detailGeneration=0;
  let failures=0;
  let lastUpdate=null;
  main.innerHTML=`<div class="page-head"><div><div class="eyebrow">Workspace</div><h1>Your inboxes</h1><p>Create an endpoint. Send an event. Inspect what arrived.</p></div><button class="button primary" id="create-inbox">Create inbox <span aria-hidden="true">+</span></button></div><div class="workspace"><aside class="inbox-sidebar" aria-label="Inboxes"><div class="sidebar-label">On this device <span id="inbox-count">0</span></div><div id="inbox-list" class="inbox-list"></div><form id="import-form" class="import-form"><label for="import-token">Have an inbox from your agent?</label><input id="import-token" placeholder="Paste its private token" autocomplete="off" required aria-describedby="import-error"><button class="button small" type="submit">Add inbox</button><span id="import-error" class="error-message" role="alert"></span></form><div class="sidebar-bottom"><span>Bookmarks stay on this device.</span><a class="inline-link" href="/connect">Connect your agent ↗</a><a class="inline-link" href="/privacy">Where events are stored ↗</a></div></aside><section id="inbox-content" class="inbox-content" aria-label="Selected inbox"></section></div>`;
  function save(){storageSet('openhook-inboxes',inboxes);}
  function renderSidebar(){
    $('#inbox-count').textContent=inboxes.length;
    $('#inbox-list').innerHTML=inboxes.length?inboxes.map(inbox=>`<button class="inbox-row" data-token="${escapeHTML(inbox.token)}" aria-current="${active?.token===inbox.token}">${icon('inbox','feature-icon')}<span><strong>${escapeHTML(inbox.name)}</strong><small>${escapeHTML(inbox.token.slice(0,8))}…</small></span></button>`).join(''):'<p class="list-empty">No saved inboxes</p>';
    $$('.inbox-row').forEach(button=>button.addEventListener('click',()=>selectInbox(inboxes.find(i=>i.token===button.dataset.token))));
  }
  function error(message){
    let box=$('#region-error');
    if(!box){box=document.createElement('div');box.id='region-error';box.className='region-error';box.setAttribute('role','alert');$('#inbox-content').prepend(box);}
    box.innerHTML=`<span class="error-message">${escapeHTML(message)}</span><button class="button small">Try again</button>`;
    $('button',box).addEventListener('click',()=>active?refresh(true):createInbox());
  }
  function clearError(){$('#region-error')?.remove();}
  function renderEmpty(){
    $('#inbox-content').innerHTML=`<div class="empty-state"><svg class="empty-mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M23 5.5A12 12 0 1 0 28 16H19"/></svg><div><h2>Give your next event a home.</h2><p>Create an inbox to receive HTTP, email, and DNS events. Or add an inbox your agent already created.</p></div><button class="button primary" id="empty-create">Create your first inbox →</button><p class="hero-note">No account needed. Capture and storage by Openhook.</p></div>`;
    $('#empty-create').addEventListener('click',createInbox);
  }
  function renderInbox(){
    const inbox=active;
    $('#inbox-content').innerHTML=`<div class="endpoint-panel"><div class="inbox-title-row"><h2>${escapeHTML(inbox.name)}</h2><div class="actions"><button class="button small ghost" id="settings">Response settings</button><button class="icon-button" id="forget" aria-label="Remove inbox bookmark from this device" title="Remove bookmark">×</button></div></div><div class="endpoint-grid">${[['HTTP',inbox.url],['Email',inbox.email],['DNS',inbox.dns],['Private token',inbox.token]].filter(([,value])=>value).map(([label,value])=>`<div class="endpoint-row"><span class="endpoint-label">${label}</span><code>${escapeHTML(value)}</code><button class="button small ghost copy-endpoint" data-copy="${escapeHTML(value)}" aria-label="Copy ${label} address">Copy</button></div>`).join('')}</div><div class="inbox-meta"><span id="expiry">${expiryLabel(inbox.expires_at)}</span><span>Keep the management token private</span></div></div><div class="event-toolbar"><div><h3>Events <span id="event-count" class="mono">—</span></h3><span id="live-status" class="live-label"><span class="dot"></span> Listening · refreshes every 5s</span></div><div class="actions"><button class="button small" id="test-event">Send test</button><button class="button small ghost" id="refresh-events" aria-label="Refresh events">Refresh</button><button class="button small ghost" id="pause-events" aria-pressed="false">Pause</button><button class="button small ghost" id="export-events">Export</button></div></div><div class="event-layout"><div id="event-list" class="event-list" role="listbox" aria-label="Captured events"><div class="skeleton long"></div><div class="skeleton short"></div></div><div id="event-detail" class="event-detail"><p class="hero-note">Select an event to inspect its payload and headers.</p></div></div><div class="event-toolbar" id="pagination" hidden><button class="button small" id="previous-page">Previous</button><span id="page-label" class="hero-note">Page 1</span><button class="button small" id="next-page">Next</button></div><div class="notice">Events are stored by Openhook. Bookmarks and private tokens stay on this device.</div>`;
    $$('.copy-endpoint').forEach(button=>button.addEventListener('click',()=>copy(button.dataset.copy,button)));
    $('#refresh-events').addEventListener('click',()=>refresh(true));
    $('#test-event').addEventListener('click',()=>testDialog());
    $('#settings').addEventListener('click',settingsDialog);
    $('#pause-events').addEventListener('click',()=>{polling=!polling;$('#pause-events').textContent=polling?'Pause':'Resume';$('#pause-events').setAttribute('aria-pressed',!polling);updateLiveStatus();if(polling)refresh();});
    $('#forget').addEventListener('click',()=>{inboxes=inboxes.filter(i=>i.token!==active.token);save();selectInbox(inboxes[0]||null);announce('Inbox bookmark removed from this device. Server events are retained.');});
    $('#export-events').addEventListener('click',exportEvents);
    $('#previous-page').addEventListener('click',()=>{if(page>1){page--;selected=null;refresh(true);}});
    $('#next-page').addEventListener('click',()=>{if(!isLast){page++;selected=null;refresh(true);}});
  }
  function expiryLabel(expiry){if(!expiry)return 'Expires according to provider limits';const date=new Date(expiry.replace(' ','T')+(expiry.includes('Z')?'':'Z'));return Number.isNaN(date.getTime())?`Expires ${expiry}`:`Expires ${date.toLocaleDateString(undefined,{month:'short',day:'numeric'})}`;}
  function updateLiveStatus(){const element=$('#live-status');if(!element)return;const text=!navigator.onLine?'Offline · showing last received events':!polling?'Paused · refresh manually':failures>=3?'Auto refresh stopped · use Refresh':failures?'Connection interrupted · retrying':`Listening · ${lastUpdate?'updated '+lastUpdate.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'}):'refreshes every 5s'}`;element.innerHTML=`<span class="dot"></span>${escapeHTML(text)}`;}
  async function selectInbox(inbox){controller?.abort();detailController?.abort();detailGeneration++;active=inbox;events=[];selected=null;page=1;failures=0;renderSidebar();if(!inbox){renderEmpty();return;}renderInbox();await refresh(true);}
  async function createInbox(){
    const button=$('#create-inbox');if(button.disabled)return;button.disabled=true;button.textContent='Creating…';$('#empty-create')?.setAttribute('disabled','');
    try {const data=await api('create');const inbox={...data,name:`Inbox ${String(inboxes.length+1).padStart(2,'0')}`};inboxes.unshift(inbox);save();await selectInbox(inbox);announce('Inbox created. Copy its URL or send a test event.');}
    catch(exc){error(`Could not create an inbox. ${exc.message}`);$('#empty-create')?.removeAttribute('disabled');}
    finally{button.disabled=false;button.innerHTML='Create inbox <span aria-hidden="true">+</span>';}
  }
  $('#create-inbox').addEventListener('click',createInbox);
  $('#import-form').addEventListener('submit',async event=>{
    event.preventDefault();const button=$('button',event.currentTarget);button.disabled=true;button.textContent='Adding…';$('#import-error').textContent='';
    try{const data=await api('info',{token:$('#import-token').value.trim()});let inbox=inboxes.find(i=>i.token===data.token);if(!inbox){inbox={...data,name:`Inbox ${String(inboxes.length+1).padStart(2,'0')}`};inboxes.unshift(inbox);save();}$('#import-token').value='';await selectInbox(inbox);announce('Inbox added.');}
    catch(exc){$('#import-error').textContent=`Could not add inbox. ${exc.message}`;}
    finally{button.disabled=false;button.textContent='Add inbox';}
  });
  async function refresh(manual=false){
    if(!active||!navigator.onLine){updateLiveStatus();return;}
    if(listLoading&&!manual)return;
    controller?.abort();const currentController=new AbortController();controller=currentController;listLoading=true;const token=active.token;const requestedPage=page;
    const button=$('#refresh-events');if(manual&&button){button.disabled=true;button.textContent='Refreshing…';}
    try{
      const data=await api('list',{token,page:requestedPage},currentController.signal);
      if(token!==active?.token||requestedPage!==page)return;
      events=data.requests||[];failures=0;lastUpdate=new Date();clearError();
      isLast=data.pagination?.is_last_page??events.length<50;
      $('#event-count').textContent=data.pagination?.total??events.length;
      renderEvents();updateLiveStatus();
      $('#pagination').hidden=page===1&&isLast;
      $('#page-label').textContent=`Page ${page}${data.pagination?.total?' · '+data.pagination.total+' events':''}`;
      $('#previous-page').disabled=page===1;$('#next-page').disabled=isLast;
      if(!selected&&events.length)await selectEvent(events[0]);
    }catch(exc){if(exc.name==='AbortError')return;if(token===active?.token){failures++;error(`Could not refresh events. ${exc.message} Your current view is retained.`);if(!events.length)$('#event-list').innerHTML='<p class="list-empty">Events unavailable. Try refreshing.</p>';updateLiveStatus();}}
    finally{if(controller===currentController){listLoading=false;if(button?.isConnected){button.disabled=false;button.textContent='Refresh';}}}
  }
  function eventLabel(event){if(event.type==='email')return event.headers?.subject?.[0]||'Incoming email';if(event.type==='dns')return 'DNS lookup';try{return new URL(event.url).pathname||'/';}catch{return event.url||'/';}}
  function eventTime(event){const date=new Date(event.created_at);return Number.isNaN(date.getTime())?'Received':date.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});}
  function renderEvents(){
    $('#event-list').innerHTML=events.length?events.map(event=>`<button class="event-row" role="option" aria-selected="${selected?.uuid===event.uuid}" data-id="${escapeHTML(event.uuid)}"><span class="event-row-top"><span class="method">${escapeHTML(event.type==='web'?event.method:event.type.toUpperCase())}</span><time class="event-time">${escapeHTML(eventTime(event))}</time></span><span class="event-path">${escapeHTML(eventLabel(event))}</span></button>`).join(''):'<div class="list-empty">No events yet.<br>Send a test or use an inbox address.</div>';
    $$('.event-row').forEach(button=>button.addEventListener('click',()=>selectEvent(events.find(event=>event.uuid===button.dataset.id))));
    $$('.event-row').forEach((button,index)=>button.addEventListener('keydown',event=>{if(!['ArrowDown','ArrowUp'].includes(event.key))return;event.preventDefault();const rows=$$('.event-row');const next=(index+(event.key==='ArrowDown'?1:-1)+rows.length)%rows.length;rows[next].focus();selectEvent(events[next]);}));
    if(!events.length){selected=null;$('#event-detail').innerHTML='<div class="empty-state"><h2>Listening for your first event.</h2><p>Use one of the addresses above, or send a test JSON payload. New events will appear here.</p><button class="button" id="detail-test">Send a test event →</button></div>';$('#detail-test').addEventListener('click',testDialog);}
  }
  async function selectEvent(event){
    if(!event)return;selected=event;renderEvents();renderDetail(event);detailController?.abort();detailController=new AbortController();const generation=++detailGeneration;const token=active.token;
    try{const data=await api('get',{token,request_id:event.uuid},detailController.signal);if(generation===detailGeneration&&token===active?.token&&selected?.uuid===event.uuid){selected=data.request||event;renderDetail(selected);}}
    catch(exc){if(exc.name!=='AbortError'&&generation===detailGeneration){const paragraph=document.createElement('p');paragraph.className='error-message';paragraph.textContent=`Could not load the full event. ${exc.message}`;$('#event-detail').append(paragraph);}}
  }
  function renderDetail(event){
    let body=event.content||event.text_content||'';try{body=JSON.stringify(JSON.parse(body),null,2);}catch{}
    $('#event-detail').innerHTML=`<div class="detail-heading"><h3>${escapeHTML(event.type==='web'?event.method:event.type.toUpperCase())} event</h3><button class="button small ghost" id="copy-body">Copy body</button></div><dl class="detail-fields"><dt>Received</dt><dd>${escapeHTML(event.created_at)}</dd><dt>Request ID</dt><dd>${escapeHTML(event.uuid)}</dd><dt>Source IP</dt><dd>${escapeHTML(event.ip)}</dd><dt>URL</dt><dd>${escapeHTML(event.url)}</dd></dl><div class="detail-block"><h4>Body</h4><pre>${escapeHTML(body||'(empty body)')}</pre></div><div class="detail-block"><h4>Headers</h4><pre>${escapeHTML(JSON.stringify(event.headers||{},null,2))}</pre></div>${Object.keys(event.query||{}).length?`<div class="detail-block"><h4>Query</h4><pre>${escapeHTML(JSON.stringify(event.query,null,2))}</pre></div>`:''}${event.html_omitted?'<p class="hero-note">Email HTML is omitted from this preview. Use export or MCP to retrieve the complete message.</p>':''}`;
    $('#copy-body').addEventListener('click',event=>copy(body,event.currentTarget));
  }
  function dialog(title,body,actionLabel,onSave){
    const previousFocus=document.activeElement;
    const element=document.createElement('dialog');element.setAttribute('aria-labelledby','dialog-title');
    element.innerHTML=`<form id="dialog-form"><div class="dialog-head"><h2 id="dialog-title">${title}</h2><button type="button" class="icon-button close-dialog" aria-label="Close dialog">×</button></div><div class="dialog-body">${body}<p id="dialog-error" class="error-message" role="alert"></p></div><div class="dialog-actions"><button type="button" class="button" id="cancel-dialog">Cancel</button><button type="submit" class="button primary" id="save-dialog">${actionLabel}</button></div></form>`;
    document.body.append(element);element.showModal();
    const close=()=>element.close();$('.close-dialog',element).addEventListener('click',close);$('#cancel-dialog').addEventListener('click',close);
    element.addEventListener('close',()=>{element.remove();if(previousFocus?.isConnected)previousFocus.focus();});
    element.addEventListener('click',event=>{if(event.target===element){const bounds=element.getBoundingClientRect();if(event.clientX<bounds.left||event.clientX>bounds.right||event.clientY<bounds.top||event.clientY>bounds.bottom)close();}});
    $('form',element).addEventListener('submit',async event=>{event.preventDefault();const button=$('#save-dialog');button.disabled=true;button.textContent='Working…';$('#dialog-error').textContent='';try{await onSave(element);close();}catch(exc){$('#dialog-error').textContent=exc.message;}finally{if(button.isConnected){button.disabled=false;button.textContent=actionLabel;}}});
  }
  function testDialog(){
    const token=active.token;
    const sample=JSON.stringify({event:'openhook.test',message:'Your agent has an inbox.',sent_at:new Date().toISOString()},null,2);
    dialog('Send a test event',`<p class="hero-note">Create a marked test JSON event. To test an external sender, send an HTTP request to the public URL.</p><label for="test-payload">JSON payload<textarea id="test-payload" rows="8" spellcheck="false">${escapeHTML(sample)}</textarea></label>`,'Send event',async()=>{
      let payload;try{payload=JSON.parse($('#test-payload').value);}catch{throw new Error('This is not valid JSON. Check the syntax and try again.');}
      if(!payload||typeof payload!=='object'||Array.isArray(payload))throw new Error('Use a JSON object for this test payload.');
      await api('send',{token,payload});if(active?.token===token){selected=null;page=1;await refresh(true);}announce('Test event sent. It may take a moment to appear.');
    });
  }
  function settingsDialog(){
    const inbox=active;const token=inbox.token;
    dialog('Response settings',`<p class="hero-note">Choose what the inbox returns to incoming HTTP requests.</p><label for="inbox-name">Name on this device<input id="inbox-name" value="${escapeHTML(inbox.name)}" maxlength="60" required></label><div class="form-row"><label for="response-status">HTTP status<input id="response-status" type="number" min="200" max="599" value="${inbox.default_status||200}" required></label><label for="response-type">Content type<select id="response-type"><option value="text/plain">text/plain</option><option value="application/json">application/json</option><option value="text/html">text/html</option></select></label></div><label for="response-body">Response body<textarea id="response-body" rows="4" maxlength="10000">${escapeHTML(inbox.default_content||'')}</textarea></label>`,'Save changes',async()=>{
      const name=$('#inbox-name').value.trim();if(!name)throw new Error('Give this inbox a name.');
      const data=await api('configure',{token,config:{default_status:Number($('#response-status').value),default_content:$('#response-body').value,default_content_type:$('#response-type').value}});
      Object.assign(inbox,data,{name});save();if(active?.token===token){renderSidebar();renderInbox();await refresh(true);}announce('Response settings saved.');
    });
    $('#response-type').value=['text/plain','application/json','text/html'].includes(inbox.default_content_type)?inbox.default_content_type:'text/plain';
  }
  async function exportEvents(event){
    const button=event.currentTarget;button.disabled=true;button.textContent='Exporting…';
    const token=active.token;
    try{const response=await fetch('/api/export',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});if(!response.ok)throw new Error((await response.json()).message||'Export failed.');const blob=await response.blob();const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=`openhook-${token.slice(0,8)}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);announce('Events exported.');}
    catch(exc){error(`Could not export events. ${exc.message}`);}
    finally{button.disabled=false;button.textContent='Export';}
  }
  renderSidebar();if(active)selectInbox(active);else renderEmpty();
  setInterval(()=>{if(polling&&!document.hidden&&navigator.onLine&&active&&failures<3)refresh();},5000);
  window.addEventListener('offline',updateLiveStatus);
  window.addEventListener('online',()=>{failures=0;updateLiveStatus();if(polling)refresh(true);});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden&&polling){failures=0;refresh();}});
}

const routes={'/':homePage,'/connect':connectPage,'/docs':docsPage,'/app':inboxPage,'/privacy':privacyPage};
const titles={'/':'Openhook — Webhook inboxes for AI agents','/connect':'Connect your agent — Openhook','/docs':'Documentation — Openhook','/app':'Your inboxes — Openhook','/privacy':'Privacy — Openhook'};
document.title=titles[location.pathname]||titles['/'];
$$('nav a').forEach(link=>{if(link.getAttribute('href')===location.pathname)link.setAttribute('aria-current','page');});
document.querySelector('link[rel=canonical]').href=`https://openhook.dev${location.pathname==='/'?'':location.pathname}`;
(routes[location.pathname]||homePage)();
