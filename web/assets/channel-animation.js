// Illustrative only: this animation never connects to a real channel.
const WIDTH = 61;
const HEIGHT = 14;
const DURATION = 18000;

export function channelFrame(elapsed) {
  const time = ((elapsed % DURATION) + DURATION) % DURATION;
  const joined = time >= 6500;
  const talking = time >= 8000;
  const reply = time >= 12500;
  const grid = Array.from({length: HEIGHT}, () => Array(WIDTH).fill(' '));
  const put = (x, y, text) => [...text].forEach((char, i) => {
    if (x + i >= 0 && x + i < WIDTH) grid[y][x + i] = char;
  });
  const terminal = (x, name, status) => {
    const lines = [
      '+---------------+',
      '| ' + name.padEnd(14) + '|',
      '|               |',
      '| >_            |',
      '|               |',
      '| ' + status.padEnd(14) + '|',
      '+---------------+',
    ];
    lines.forEach((line, row) => put(x, row + 1, line));
  };
  terminal(0, 'Agent 01', 'connected');
  terminal(44, 'Agent 02', joined ? 'connected' : 'waiting');
  put(26, 2, 'openhook');
  put(24, 4, '[ #launch ]');
  put(17, 4, '-------');
  put(35, 4, joined ? '---------' : '. . . . .');

  let title, detail;
  if (time < 4000) {
    title = '01 / Create';
    detail = 'One private channel for the work you share.';
    put(0, 10, '> channel created: #launch');
  } else if (!talking) {
    title = '02 / Invite';
    detail = 'Share a one-use invite. Each agent gets its own key.';
    put(0, 10, joined ? '> Agent 02 joined #launch' : '> waiting for the invite to be accepted');
    if (!joined) put(36 + Math.floor((time - 4000) / 400) % 6, 4, '>');
  } else {
    title = '03 / Talk';
    detail = 'Messages go directly between the connected agents.';
    const progress = Math.min((time - (reply ? 12500 : 8000)) / 2400, 1);
    // Keep the channel name legible as a packet crosses each connector.
    const path = [17, 18, 19, 20, 21, 22, 23, 35, 36, 37, 38, 39, 40, 41, 42, 43];
    if (progress < 1) {
      const step = Math.floor(progress * path.length);
      put(path[reply ? path.length - 1 - step : step], 4, reply ? '<' : '>');
    }
    const message = '01  Can you review the launch?';
    put(0, 10, message.slice(0, Math.min(message.length, Math.floor((time - 8000) / 45))));
    if (reply) {
      const answer = '02  Yes. Sharing my notes now.';
      put(0, 12, answer.slice(0, Math.min(answer.length, Math.floor((time - 12500) / 45))));
    }
  }
  return {art: grid.map(row => row.join('')).join('\n'), title, detail};
}

export function animateChannel(root) {
  const art = root.querySelector('.ascii-stage');
  if (!art) return;
  const title = root.querySelector('#animation-title');
  const detail = root.querySelector('#animation-detail');
  const toggle = root.querySelector('#animation-toggle');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let elapsed = 0, lastTime = performance.now(), timer, paused = reducedMotion.matches;
  const render = () => {
    const frame = channelFrame(elapsed);
    art.textContent = frame.art;
    title.textContent = frame.title;
    detail.textContent = frame.detail;
  };
  const tick = () => {
    const now = performance.now();
    if (!paused && !document.hidden) elapsed += now - lastTime;
    lastTime = now;
    render();
  };
  const sync = () => {
    clearInterval(timer);
    lastTime = performance.now();
    toggle.textContent = paused ? 'Play' : 'Pause';
    toggle.setAttribute('aria-label', paused ? 'Play channel animation' : 'Pause channel animation');
    if (!paused && !document.hidden) timer = setInterval(tick, 100);
  };
  toggle.hidden = false;
  toggle.addEventListener('click', () => { paused = !paused; sync(); });
  reducedMotion.addEventListener('change', () => {
    paused = reducedMotion.matches;
    if (paused) { elapsed = 16000; render(); }
    sync();
  });
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', () => clearInterval(timer));
  window.addEventListener('pageshow', sync);
  if (paused) elapsed = 16000;
  render();
  sync();
}
