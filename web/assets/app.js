import {renderHome} from './home.js?v=d585ad698949';
'use strict';

const main = document.querySelector('#main');
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const escapeHTML = (value = '') => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const origin = location.origin;
const announce = text => { $('#announcement').textContent = text; };
function storageGet(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } }
function storageSet(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { announce('Browser storage is unavailable. Copy your private token before leaving.'); return false; } }
function updateThemeButton() {
  const isDark = document.documentElement.dataset.theme === 'dark';
  $('#theme-toggle').textContent = isDark ? 'Light' : 'Dark';
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

function homePage() { renderHome(main, {origin, copy, api, storageGet, storageSet}); }

function enhanceCopyButtons() {
  $$('.copy-code', main).forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => copy(button.previousElementSibling.textContent, button));
  });
}

function docsPage() {
  const search = $('#tool-search');
  const rows = $$('.tool-row');
  search.closest('label').hidden = false;
  search.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    let matches = 0;
    rows.forEach(row => {
      row.hidden = !row.textContent.toLowerCase().includes(query);
      if (!row.hidden) matches++;
    });
    $('#tool-empty').hidden = matches > 0;
  });
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
  main.innerHTML=`<div class="page-head"><div><div class="eyebrow">Workspace</div><h1>Your inboxes</h1><p>Create a webhook URL. Read what arrives.</p></div><button class="button primary" id="create-inbox">Create inbox <span aria-hidden="true">+</span></button></div><div class="workspace"><aside class="inbox-sidebar" aria-label="Inboxes"><div class="sidebar-label">On this device <span id="inbox-count">0</span></div><div id="inbox-list" class="inbox-list"></div><form id="import-form" class="import-form"><label for="import-token">Have an inbox from your agent?</label><input id="import-token" placeholder="Paste its private token" autocomplete="off" required aria-describedby="import-error"><button class="button small" type="submit">Add inbox</button><span id="import-error" class="error-message" role="alert"></span></form><div class="sidebar-bottom"><span>Bookmarks stay on this device.</span><a class="inline-link" href="/connect">Connect your agent ↗</a><a class="inline-link" href="/privacy">Where events are stored ↗</a></div></aside><section id="inbox-content" class="inbox-content" aria-label="Selected inbox"></section></div>`;
  function save(){storageSet('openhook-inboxes',inboxes);}
  function renderSidebar(){
    $('#inbox-count').textContent=inboxes.length;
    $('#inbox-list').innerHTML=inboxes.length?inboxes.map(inbox=>`<button class="inbox-row" data-token="${escapeHTML(inbox.token)}" aria-current="${active?.token===inbox.token}"><span><strong>${escapeHTML(inbox.name)}</strong><small>${escapeHTML(inbox.token.slice(0,8))}…</small></span></button>`).join(''):'<p class="list-empty">No saved inboxes</p>';
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
    $('#inbox-content').innerHTML=`<div class="empty-state"><div><h2>Create your first inbox.</h2><p>Create a webhook URL, or add an inbox your agent already created.</p></div><button class="button primary" id="empty-create">Create your first inbox →</button><p class="hero-note">No account needed. Capture and storage by Openhook.</p></div>`;
    $('#empty-create').addEventListener('click',createInbox);
  }
  function renderInbox(){
    const inbox=active;
    $('#inbox-content').innerHTML=`<div class="endpoint-panel"><div class="inbox-title-row"><h2>${escapeHTML(inbox.name)}</h2><div class="actions"><button class="button small ghost" id="settings">Response settings</button><button class="icon-button" id="forget" aria-label="Remove inbox bookmark from this device" title="Remove bookmark">Remove</button></div></div><div class="endpoint-grid">${[['HTTP',inbox.url],['Email',inbox.email],['DNS',inbox.dns],['Private token',inbox.token]].filter(([,value])=>value).map(([label,value])=>`<div class="endpoint-row"><span class="endpoint-label">${label}</span><code>${escapeHTML(value)}</code><button class="button small ghost copy-endpoint" data-copy="${escapeHTML(value)}" aria-label="Copy ${label} address">Copy</button></div>`).join('')}</div><div class="inbox-meta"><span id="expiry">${expiryLabel(inbox.expires_at)}</span><span>Keep the management token private</span></div></div><div class="event-toolbar"><div><h3>Events <span id="event-count" class="mono">—</span></h3><span id="live-status" class="live-label"><span class="dot"></span> Listening · refreshes every 5s</span></div><div class="actions"><button class="button small" id="test-event">Send test</button><button class="button small ghost" id="refresh-events" aria-label="Refresh events">Refresh</button><button class="button small ghost" id="pause-events" aria-pressed="false">Pause</button><button class="button small ghost" id="export-events">Export</button></div></div><div class="event-layout"><div id="event-list" class="event-list" role="listbox" aria-label="Captured events"><p class="quiet">Loading events…</p></div><div id="event-detail" class="event-detail"><p class="hero-note">Select an event to inspect its payload and headers.</p></div></div><div class="event-toolbar" id="pagination" hidden><button class="button small" id="previous-page">Previous</button><span id="page-label" class="hero-note">Page 1</span><button class="button small" id="next-page">Next</button></div><section class="reading" aria-labelledby="activity-title"><h3 id="activity-title">Activity</h3><p class="quiet">Receipts and changes, in order. Payloads and secrets are excluded.</p><div id="activity-list" class="reading"></div><button class="button small" id="load-activity">Load activity</button><p id="activity-status" class="quiet" role="status"></p></section><div class="notice">Events are stored by Openhook. Bookmarks and private tokens stay on this device.</div>`;
    $$('.copy-endpoint').forEach(button=>button.addEventListener('click',()=>copy(button.dataset.copy,button)));
    $('#refresh-events').addEventListener('click',()=>refresh(true));
    $('#test-event').addEventListener('click',()=>testDialog());
    $('#settings').addEventListener('click',settingsDialog);
    let activitySince = 0;
    $('#load-activity').addEventListener('click', async event => {
      const button = event.currentTarget;
      const list = $('#activity-list');
      const status = $('#activity-status');
      button.disabled = true;
      try {
        const result = await api('activity', {token: inbox.token, since: activitySince, limit: 50});
        if (active?.token !== inbox.token) return;
        if (activitySince === 0) list.replaceChildren();
        for (const item of result.activity) {
          const row = document.createElement('p');
          row.className = 'quiet';
          row.textContent = item.created_at + ' · ' + item.action + (item.details.type ? ' · ' + item.details.type : '');
          list.append(row);
        }
        status.textContent = result.has_more ? 'More activity is available.' : 'Activity is up to date.';
        activitySince = result.has_more ? result.next_since : 0;
        button.textContent = result.has_more ? 'Load more activity' : 'Refresh activity';
      } catch (error) {
        if (active?.token === inbox.token) status.textContent = error.message;
      } finally { button.disabled = false; }
    });
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
    element.innerHTML=`<form id="dialog-form"><div class="dialog-head"><h2 id="dialog-title">${title}</h2><button type="button" class="icon-button close-dialog" aria-label="Close dialog">Close</button></div><div class="dialog-body">${body}<p id="dialog-error" class="error-message" role="alert"></p></div><div class="dialog-actions"><button type="button" class="button" id="cancel-dialog">Cancel</button><button type="submit" class="button primary" id="save-dialog">${actionLabel}</button></div></form>`;
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

enhanceCopyButtons();
$('#theme-toggle').hidden = false;
$$('nav a').forEach(link => {
  if (link.getAttribute('href') === location.pathname) link.setAttribute('aria-current', 'page');
});
const routes = {'/': homePage, '/docs': docsPage, '/app': inboxPage};
routes[location.pathname]?.();
