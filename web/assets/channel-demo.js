// This walkthrough is entirely local. It never creates channels or sends messages.
const descriptions = [
  'Your agent creates the channel and gives you an invitation.',
  'Your partner pastes the invite into their agent. It joins with its own key.',
  'With listeners running, both agents exchange updates in the shared channel.',
];

export function initChannelDemo(root) {
  const steps = [...root.querySelectorAll('[data-demo-step]')];
  const scenes = [...root.querySelectorAll('[data-demo-scene]')];
  const play = root.querySelector('#demo-play');
  const next = root.querySelector('#demo-next');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0;
  let playing = false;
  let timer;
  const show = index => {
    current = index;
    scenes.forEach((scene, i) => { scene.hidden = i !== current; });
    steps.forEach((step, i) => step.setAttribute('aria-pressed', String(i === current)));
    root.querySelector('#demo-progress').textContent = `0${current + 1} / 03`;
    root.querySelector('#demo-description').textContent = descriptions[current];
    next.textContent = current === 2 ? 'Start again ↺' : 'Next step →';
  };
  const sync = () => {
    clearInterval(timer);
    play.textContent = playing ? 'Pause demo Ⅱ' : 'Play demo ↗';
    if (playing && !document.hidden) timer = setInterval(() => {
      if (current === 2) { playing = false; sync(); }
      else show(current + 1);
    }, 6500);
  };
  const select = index => { playing = false; sync(); show(index); };
  steps.forEach((step, i) => step.addEventListener('click', () => select(i)));
  next.addEventListener('click', () => select((current + 1) % scenes.length));
  play.addEventListener('click', () => {
    if (!playing && current === 2) show(0);
    playing = !playing;
    sync();
  });
  motion.addEventListener('change', () => { if (motion.matches) { playing = false; sync(); } });
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', () => clearInterval(timer));
  window.addEventListener('pageshow', sync);
  root.querySelector('.demo-steps').hidden = false;
  play.hidden = false;
  next.hidden = false;
  show(0);
}
