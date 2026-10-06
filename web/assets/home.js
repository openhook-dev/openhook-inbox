import {animateDither,wipeDither} from './dither.js?v=ee6687f1c6f6';

const scenes = {
  http: {label:'HTTP webhook', source:'GitHub → Openhook', tool:'register_github_webhook()', event:'push', method:'POST', body:{event:'push', repository:'your-project', ref:'refs/heads/main'}, next:'The push arrived. Review the changes.'},
  email: {label:'Email inbox', source:'SMTP → Openhook', tool:'create_webhook()', event:'email.received', method:'SMTP', body:{subject:'Confirm your email', code:'482901', to:'task@mail.openhook.dev'}, next:'The email arrived. Continue verification.'},
  dns: {label:'DNS callback', source:'DNS → Openhook', tool:'generate_oob_payloads()', event:'dns.query', method:'DNS', body:{query:'check.task.dns.openhook.dev', type:'A', transport:'UDP'}, next:'The lookup arrived. Inspect the callback.'},
};

function architecture() {
  const tiles = Array.from({length:36},(_,i)=>`<rect x="${60+(i%12)*25}" y="${25+Math.floor(i/12)*25}" width="17" height="17"/>`).join('');
  return `<svg viewBox="0 0 900 420" role="img" aria-labelledby="flow-title"><title id="flow-title">HTTP, email, and DNS flow through a durable Openhook inbox into your agent</title><g class="flow-lines" fill="none" stroke="currentColor"><path d="M100 88H400V160M790 88H500V160M450 250V344H750"/><path class="flow-packet" d="M100 88H400V160M790 88H500V160M450 250V344H750"/></g><g class="flow-layer" transform="translate(210 228)"><path d="M0 0 240-104 480 0 240 104Z" fill="var(--raised)" stroke="var(--line-2)"/><path d="M0 0V12L240 116V104Z" fill="var(--frame)" stroke="var(--line-2)"/><path d="M240 104V116L480 12V0Z" fill="var(--frame)" stroke="var(--line-2)"/></g><g class="flow-layer signal-layer" transform="translate(210 190)"><path d="M0 0 240-104 480 0 240 104Z" fill="var(--accent)"/><path d="M0 0V12L240 116V104Z" fill="var(--fg-2)"/><path d="M240 104V116L480 12V0Z" fill="var(--fg-3)"/></g><g class="flow-layer" transform="translate(210 147)"><path d="M0 0 240-104 480 0 240 104Z" fill="var(--page)" stroke="var(--line-2)"/><g transform="matrix(1 .433 -1 .433 225 -95)" fill="var(--line-2)">${tiles}</g><path d="M0 0V12L240 116V104Z" fill="var(--frame)" stroke="var(--line-2)"/><path d="M240 104V116L480 12V0Z" fill="var(--frame)" stroke="var(--line-2)"/></g><g class="flow-labels" fill="currentColor"><text x="100" y="68">EXTERNAL EVENTS</text><text x="708" y="68">PRIVATE TOKEN</text><text x="670" y="374">YOUR AGENT</text></g><rect class="flow-node" x="98" y="85" width="7" height="7"/><rect class="flow-node" x="786" y="85" width="7" height="7"/><rect class="flow-node" x="746" y="340" width="7" height="7"/></svg>`;
}

export function renderHome(main, {origin, copy}) {
  main.classList.add('landing');
  main.innerHTML = `
    <section class="signal-hero" aria-labelledby="hero-title">
      <canvas class="signal-field live-dither" aria-hidden="true"></canvas>
      <div class="landing-wrap hero-grid">
        <div class="signal-copy"><p class="bracket-label">[ THE AGENT INBOX ]</p><h1 id="hero-title">AN INBOX FOR<br>YOUR AI AGENT.</h1><p>Your agent sends a request. Openhook catches what comes back. Webhooks, emails, and DNS callbacks—in one place.</p><div class="actions"><a class="button primary" href="/app">CREATE AN INBOX <span aria-hidden="true">↗</span></a><a class="button" href="/connect">CONNECT YOUR AGENT <span aria-hidden="true">→</span></a></div><button class="setup-command" id="quick-connect"><span aria-hidden="true">▣</span> COPY AGENT SETUP</button></div>
        <div class="signal-demo" aria-label="Interactive Openhook workflow preview">
          <div class="demo-top"><span class="demo-id"><span class="square-dot"></span> task_42 <span class="dim">/ inbox</span></span><button id="demo-pause" class="icon-button" aria-label="Pause workflow animation">Ⅱ</button><span class="demo-tag">WORKFLOW PREVIEW</span></div>
          <div class="demo-scene"><div id="workflow-scene">${architecture()}</div><canvas class="scene-wipe" aria-hidden="true"></canvas></div>
          <div class="demo-panels"><div class="demo-terminal"><div class="demo-log" id="demo-log"></div><span class="terminal-cursor" aria-hidden="true">▌</span></div><div class="demo-event"><div class="event-preview"><div class="event-preview-bar"><span id="demo-method">POST</span><span id="demo-event-name">push</span></div><pre id="demo-body"></pre></div><div class="agent-response" id="demo-response"></div></div></div>
          <div class="demo-progress" aria-hidden="true"><span></span></div>
          <div class="demo-status"><span id="demo-source">GitHub → Openhook</span><span id="demo-state"><span class="square-dot"></span> LISTENING</span></div>
          <div class="demo-tabs" role="tablist" aria-label="Event protocol">${Object.entries(scenes).map(([key,s],i)=>`<button role="tab" id="demo-tab-${key}" aria-selected="${i===0}" aria-controls="demo-log" tabindex="${i===0?0:-1}" data-scene="${key}">${s.label}<span aria-hidden="true">↗</span></button>`).join('')}</div>
        </div>
      </div>
    </section>
    <section class="protocol-band" aria-label="Supported protocols and clients"><div class="landing-wrap"><p class="bracket-label">ONE INBOX · THREE PROTOCOLS · ANY MCP CLIENT</p><div class="protocol-names"><span>HTTP</span><span>SMTP</span><span>DNS</span><span class="protocol-divider"></span><span>Claude Code</span><span>Cursor</span><span>VS Code</span><span>OpenClaw</span></div></div></section>
    <section class="landing-section landing-wrap" id="platform"><div class="section-intro reveal"><p class="bracket-label">[ TRY IT NOW ]</p><h2>SEND AN EVENT.<br><strong>SEE IT ARRIVE.</strong></h2><p>Press Send to try Openhook. We'll create an inbox, send a real webhook, and show you exactly what arrived.</p></div><div class="architecture reveal" id="event-relay">${architecture()}<p class="relay-loading">Loading the interactive event relay…</p></div></section>
    <section class="landing-section use-section" id="workflows"><div class="landing-wrap"><div class="section-intro reveal"><p class="bracket-label">[ THREE WAYS IN ]</p><h2>WHATEVER THE REPLY.<br>ONE INBOX.</h2><p>A build finishes. An email arrives. A server looks up an address. Your agent gets the event and carries on.</p></div><div class="workflow-grid">
      <a class="workflow-card reveal" href="/docs"><div class="workflow-art art-web" aria-hidden="true"><span class="art-label">SOURCE / GITHUB</span><span class="wire"></span><span class="mini-event">POST <b>push</b><br><i>200 · captured</i></span><div class="pixel-cloud"></div></div><span class="bracket-label">01 / WEBHOOKS</span><h3>The build finished.<br>Your agent can move on.</h3><p>Catch updates from GitHub, Stripe, or Linear. Your agent reads the webhook and carries on.</p><span class="card-link">EXPLORE WEBHOOK TOOLS ↗</span></a>
      <a class="workflow-card reveal" href="/docs"><div class="workflow-art art-mail" aria-hidden="true"><span class="art-label">INBOX / TEMPORARY</span><div class="pixel-envelope">✉</div><span class="code-digits">4 8 2 9 0 1</span></div><span class="bracket-label">02 / EMAIL</span><h3>The code arrived.<br>The task keeps moving.</h3><p>Give your agent an email address. Read messages, links, and verification codes as they arrive.</p><span class="card-link">EXPLORE EMAIL TOOLS ↗</span></a>
      <a class="workflow-card reveal" href="/docs"><div class="workflow-art art-dns" aria-hidden="true"><span class="art-label">CALLBACK / DNS</span><div class="dns-orbit"><span></span><span></span><span></span><b>↗</b></div><span class="dns-name">check.task.dns.openhook.dev</span></div><span class="bracket-label">03 / DNS</span><h3>The lookup happened.<br>Now you have the proof.</h3><p>See when a system looks up your task’s DNS address. Keep the result with your other events.</p><span class="card-link">EXPLORE CALLBACK TOOLS ↗</span></a>
    </div></div></section>
    <section class="landing-section landing-wrap"><div class="section-intro reveal"><p class="bracket-label">[ THE INBOX ]</p><h2>CREATE. WAIT. READ.<br>KEEP GOING.</h2><p>Give your agent an address, wait for a reply, and read what arrived.</p></div><div class="capability-grid">
      ${[['01','Create on demand','Get a webhook URL, email address, and DNS name. No account needed.','create_webhook()'],['02','Register at the source','Subscribe to GitHub, Stripe, or Linear. Provider credentials are never saved.','register_github_webhook()'],['03','Wait, then continue','Wait for the next reply. Pick up where you left off after reconnecting.','wait_for_request()'],['04','Inspect every byte','Read the full message. Search, add notes, or export your events.','get_request()'],['05','Keep control','Share your inbox address. Keep its reading key private. Delete it when you’re done.','rotate_webhook_token()'],['06','Bring it home','Send events to a local app or a running OpenClaw agent.','openhook-listen --forward']].map(([n,title,body,code])=>`<article class="capability reveal"><span class="bracket-label">[ ${n} ]</span><h3>${title}</h3><p>${body}</p><code>${code}</code></article>`).join('')}
    </div></section>
    <section class="deployment-section landing-section"><div class="landing-wrap deployment-grid"><div class="section-intro reveal"><p class="bracket-label">[ HOSTED OR SELF-HOSTED ]</p><h2>YOUR EVENTS.<br>YOUR INFRASTRUCTURE.</h2><p>Use our hosted service, or run Openhook on your own server. Your agent connects the same way.</p><a class="button" href="https://github.com/openhook-dev/openhook-inbox" target="_blank" rel="noopener noreferrer">EXPLORE THE SOURCE ↗</a></div><div class="deploy-options reveal"><details open><summary>Openhook Cloud <span class="availability">AVAILABLE</span></summary><p>Connect to the hosted MCP endpoint. Create an inbox and send your first event.</p><code>${origin}/mcp</code><a class="inline-link" href="/connect">CONNECT YOUR AGENT →</a></details><details><summary>Self-hosted <span class="availability">MIT LICENSE</span></summary><p>Run HTTP, SMTP, DNS, and MCP on your own server. Docker Compose and Dokploy deployment files are included.</p><code>uv run openhook --http</code><a class="inline-link" href="https://github.com/openhook-dev/openhook-inbox/blob/main/docs/deployment.md" target="_blank" rel="noopener noreferrer">READ DEPLOYMENT DOCS ↗</a></details></div></div></section>
    <section class="spec-band"><div class="landing-wrap spec-grid">${[['26','MCP TOOLS'],['3','INBOUND PROTOCOLS'],['7 DAYS','MAXIMUM INBOX LIFETIME'],['MIT','OPEN SOURCE']].map(([v,l])=>`<div><strong>${v}</strong><span>${l}</span></div>`).join('')}</div></section>
    <section class="landing-section landing-wrap faq-section"><div class="section-intro reveal"><p class="bracket-label">[ BEFORE YOU CONNECT ]</p><h2>A FEW GOOD<br>QUESTIONS.</h2></div><div class="faq-list reveal">${[['Do I need an account?','No. Create an anonymous inbox in the browser or through MCP. Save its private management token to read the events later.'],['Can an event wake my agent?','MCP waits return events to a running agent. The local Openhook listener can also send a wakeup to a configured OpenClaw agent. A client that has exited needs a running listener or runtime integration.'],['How long do events stay?','Inboxes expire within seven days. Each keeps its latest 1000 events, with a 1 MB limit per event. Export what you need before the inbox expires.'],['Are provider credentials stored?','No. API credentials are used only for registration and removal calls. Signing secrets are stored so Openhook can verify incoming events. Unregister source subscriptions before the inbox expires.'],['Can I use my local server?','Yes. Run openhook-listen --forward with your local callback URL. The listener connects outward, forwards original event bodies, and saves its cursor after successful delivery.']].map(([q,a])=>`<details><summary>${q}<span aria-hidden="true">+</span></summary><p>${a}</p></details>`).join('')}</div></section>
    <section class="closing-section"><img class="closing-field" src="/assets/signal-field.svg" alt="" aria-hidden="true"><div class="landing-wrap reveal"><p class="bracket-label">[ READY FOR THE NEXT EVENT ]</p><h2>LET YOUR AGENT<br>HEAR BACK.</h2><div class="actions"><a class="button primary" href="/app">CREATE YOUR FIRST INBOX ↗</a><a class="button" href="/connect">CONNECT VIA MCP →</a></div><p class="closing-note">HTTP / EMAIL / DNS · OPEN SOURCE · NO ACCOUNT REQUIRED</p></div></section>`;

  const command = `claude mcp add --transport http openhook ${origin}/mcp`;
  main.querySelector('#quick-connect').addEventListener('click',event=>copy(command,event.currentTarget));
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let active = 'http', step = 0, paused = reduced, timer, visible=false, workflow;
  const field=animateDither(main.querySelector('.live-dither'));
  const figure=import('/assets/iso/figure.js?v=6c81da1bc59e');
  figure.then(module=>{workflow=module.mountWorkflow(main.querySelector('#workflow-scene'),value=>{step=value;paused=true;draw();updatePause();schedule();});draw();}).catch(()=>{});
  const log = main.querySelector('#demo-log');
  function draw() {
    const scene = scenes[active];
    const lines = [`<span class="log-command">$ ${scene.tool}</span>`,`<span class="log-ok">✓ inbox ready</span> <span class="dim">task_42</span>`,`agent&gt; wait_for_request(token)`,`<span class="dim">listening for ${scene.label.toLowerCase()}…</span>`,`<span class="log-ok">✓ ${scene.event} received</span>`,`agent&gt; inspect event`,`<span class="log-accent">↳ task resumed</span>`];
    log.innerHTML = lines.map((line,i)=>`<div class="log-line ${i<=step?'visible':''}">${line}</div>`).join('');
    main.querySelector('#demo-body').textContent = JSON.stringify(scene.body,null,2);
    main.querySelector('#demo-method').textContent = scene.method;
    main.querySelector('#demo-event-name').textContent = scene.event;
    main.querySelector('#demo-source').textContent = scene.source;
    main.querySelector('#demo-state').innerHTML = `<span class="square-dot"></span> ${step>=4?'CAPTURED':'LISTENING'}`;
    main.querySelector('#demo-response').textContent = step>=6?scene.next:'Agent waiting for an event…';
    main.querySelector('.signal-demo').classList.toggle('event-arrived',step>=4);
    main.querySelector('.signal-demo').dataset.step=step;
    main.querySelector('.demo-progress span').style.width=`${(step+1)/9*100}%`;
    workflow?.update(active,step,paused);
  }
  function schedule() { clearInterval(timer); if(!paused&&visible&&!document.hidden) timer=setInterval(()=>{step=(step+1)%9;draw();},1050); }
  function select(key) { active=key;step=paused?6:0;wipeDither(main.querySelector('.scene-wipe'));main.querySelectorAll('[data-scene]').forEach(tab=>{const selected=tab.dataset.scene===key;tab.setAttribute('aria-selected',selected);tab.tabIndex=selected?0:-1;});draw();schedule(); }
  const tabs = [...main.querySelectorAll('[data-scene]')];
  tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>select(tab.dataset.scene));tab.addEventListener('keydown',e=>{let j;if(e.key==='ArrowRight')j=(i+1)%tabs.length;if(e.key==='ArrowLeft')j=(i-1+tabs.length)%tabs.length;if(e.key==='Home')j=0;if(e.key==='End')j=tabs.length-1;if(j!==undefined){e.preventDefault();tabs[j].focus();select(tabs[j].dataset.scene);}});});
  const pause = main.querySelector('#demo-pause');
  function updatePause() {pause.textContent=paused?'▶':'Ⅱ';pause.setAttribute('aria-label',paused?'Play workflow animation':'Pause workflow animation');main.querySelector('.signal-demo').classList.toggle('demo-paused',paused);field.pause(paused);workflow?.update(active,step,paused);}
  pause.addEventListener('click',()=>{paused=!paused;updatePause();schedule();});
  const demoObserver=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;schedule();});demoObserver.observe(main.querySelector('.signal-demo'));
  document.addEventListener('visibilitychange',()=>{if(document.hidden)clearInterval(timer);else schedule();});
  const revealObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('in-view');revealObserver.unobserve(entry.target);}}),{threshold:.08});
  main.querySelectorAll('.reveal').forEach(el=>revealObserver.observe(el));
  const relay=main.querySelector('#event-relay');
  const relayObserver=new IntersectionObserver(entries=>{if(entries[0].isIntersecting){relayObserver.disconnect();figure.then(module=>module.mountRelay(relay)).catch(()=>{relay.querySelector('.relay-loading').textContent='The interactive relay could not load. Refresh this page to try again.';});}},{rootMargin:'160px'});
  relayObserver.observe(relay);
  if(reduced)step=6;draw();updatePause();schedule();
}
