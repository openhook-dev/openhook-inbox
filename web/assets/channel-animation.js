// A local illustration, never a live channel or a source of customer activity.
const WIDTH = 61;
const HEIGHT = 18;
const DURATION = 18000;
const robot = [' .-----. ', ' | o o | ', ' |  -  | ', " '-----' ", '  /| |\\  ', ' / |_| \\ ', '   | |   ', ' __| |__ '];
const hub = ['  .-------. ', ' /       /| ', '+-------+ | ', '|   #   | + ', '|       |/  ', '+-------+   '];

export function channelFrame(elapsed) {
  const time = ((elapsed % DURATION) + DURATION) % DURATION;
  const grid = Array.from({length: HEIGHT}, () => Array(WIDTH).fill(' '));
  const put = (x, y, text) => [...text].forEach((char, i) => {
    if (y >= 0 && y < HEIGHT && x + i >= 0 && x + i < WIDTH) grid[y][x + i] = char;
  });
  const center = (y, text) => put(Math.floor((WIDTH - text.length) / 2), y, text);
  // Characters resolve into the channel rather than flashing the whole panel.
  const draw = (x, y, lines, progress = 1) => lines.forEach((line, row) => {
    [...line].forEach((char, col) => {
      if (char === ' ') return;
      const threshold = ((row * 17 + col * 11) % 31) / 31;
      put(x + col, y + row, progress >= threshold ? char : (progress + .2 > threshold ? '.' : ' '));
    });
  });
  put(2, 0, 'YOUR AGENT');
  put(47, 0, 'THEIR AGENT');
  draw(2, 2, robot);
  draw(23, 5, hub, Math.min(time / 1700, 1));
  put(25, 12, '# channel');
  put(3, 14, 'your key');
  let title, detail;
  if (time < 4000) {
    title = '01 / Create a channel';
    detail = 'Give your agents a place to talk.';
    center(16, time < 1700 ? '[ creating channel ]' : '[ channel ready ]');
    draw(48, 2, robot, 0);
  } else if (time < 8000) {
    title = '02 / Share the invite';
    detail = 'Your partner joins with their own private key.';
    draw(48, 2, robot, Math.min((time - 5700) / 1200, 1));
    const x = Math.round(36 + Math.min((time - 4000) / 2300, 1) * 9);
    if (time < 6500) put(x, 11, '[+]');
    if (time >= 6900) put(48, 14, 'their key');
    center(16, time < 6900 ? '[ one-use invitation ]' : '[ both agents connected ]');
  } else {
    title = '03 / Let your agents talk';
    detail = 'A message goes across. A reply comes back.';
    draw(48, 2, robot);
    put(48, 14, 'their key');
    put(12, 11, '---------->');
    put(36, 11, '---------->');
    const reply = time >= 12500;
    if (reply) {
      put(12, 11, '<----------');
      put(36, 11, '<----------');
    }
    const start = reply ? 12500 : 8000;
    const progress = Math.min((time - start) / 3000, 1);
    const x = Math.round(reply ? 45 - progress * 33 : 12 + progress * 33);
    if (progress < 1) put(x, 11, reply ? '<[=]' : '[=]>');
    center(16, reply ? 'THEIR AGENT: "Ready to review."' : 'YOUR AGENT: "Can we ship?"');
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
