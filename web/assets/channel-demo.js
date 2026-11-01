// A demonstration, never a connection to a real channel.
export function initChannelDemo(root) {
  const messages = [...root.querySelectorAll('[data-story-message]')];
  const replay = root.querySelector('#story-replay');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let visible = messages.length;
  let timer;
  const render = () => {
    messages.forEach((message, index) => {
      const pending = index >= visible;
      message.classList.toggle('pending', pending);
      if (pending) message.setAttribute('aria-hidden', 'true');
      else message.removeAttribute('aria-hidden');
    });
    root.querySelector('.story-end p').classList.toggle('pending', visible < messages.length);
    replay.textContent = visible < messages.length ? 'Show all ↓' : 'Replay ↻';
  };
  const finish = () => {
    clearTimeout(timer);
    visible = messages.length;
    render();
  };
  const advance = () => {
    clearTimeout(timer);
    if (document.hidden || motion.matches) { finish(); return; }
    render();
    if (visible < messages.length) timer = setTimeout(() => { visible++; advance(); }, 2200);
  };
  const start = () => { visible = 1; advance(); };
  replay.addEventListener('click', () => {
    if (visible < messages.length) finish();
    else start();
  });
  motion.addEventListener('change', finish);
  document.addEventListener('visibilitychange', finish);
  window.addEventListener('pagehide', finish);
  replay.hidden = false;
  start();
}
