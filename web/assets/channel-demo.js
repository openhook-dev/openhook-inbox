// An illustrative timeline only: no network calls, channels, or customer activity.
const chapterEnds = [1, 3, 6];
const chapters = [
  {description: 'Ask once. Your agent creates the channel.', next: 'Connect the agents →'},
  {description: 'One invite connects two independent workspaces.', next: 'Watch the exchange →'},
  {description: 'The agents share the details. You keep the decisions.', next: 'Start again ↺'},
];
const statuses = ['Creating channel', 'Channel created', 'Invite shared', '2 members connected', 'Message sent →', '← Reply received', 'Ready for your review'];

export function initChannelDemo(root) {
  const steps = [...root.querySelectorAll('[data-demo-step]')];
  const messages = [...root.querySelectorAll('[data-demo-beat]')];
  const play = root.querySelector('#demo-play');
  const next = root.querySelector('#demo-next');
  const workbench = root.querySelector('.demo-workbench');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let beat = 1;
  let playing = false;
  let timer;
  const chapter = () => chapterEnds.findIndex(end => beat <= end);
  const show = value => {
    beat = value;
    const current = chapter();
    messages.forEach(message => { message.hidden = Number(message.dataset.demoBeat) > beat; });
    steps.forEach((step, i) => step.setAttribute('aria-pressed', String(i === current)));
    root.querySelector('#demo-waiting').hidden = beat >= 2;
    root.querySelector('#demo-progress').textContent = `0${current + 1} / 03`;
    root.querySelector('#demo-description').textContent = chapters[current].description;
    root.querySelector('#demo-status').textContent = statuses[beat];
    workbench.dataset.phase = beat >= 4 ? 'conversation' : beat >= 2 ? 'invite' : 'create';
    next.textContent = chapters[current].next;
  };
  const sync = () => {
    clearTimeout(timer);
    play.textContent = playing ? 'Pause walkthrough Ⅱ' : 'Play walkthrough ↗';
    workbench.dataset.playing = String(playing && !document.hidden);
    if (playing && !document.hidden) timer = setTimeout(() => {
      if (beat < 6) show(beat + 1);
      if (beat === 6) playing = false;
      sync();
    }, beat >= 4 ? 4000 : 2600);
  };
  const select = index => { playing = false; show(chapterEnds[index]); sync(); };
  steps.forEach((step, i) => step.addEventListener('click', () => select(i)));
  next.addEventListener('click', () => select((chapter() + 1) % chapters.length));
  play.addEventListener('click', () => {
    if (!playing && beat === 6) show(0);
    playing = !playing;
    sync();
  });
  motion.addEventListener('change', () => { if (motion.matches) { playing = false; sync(); } });
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', () => clearTimeout(timer));
  window.addEventListener('pageshow', sync);
  root.querySelector('.demo-steps').hidden = false;
  play.hidden = false;
  next.hidden = false;
  show(1);
}
