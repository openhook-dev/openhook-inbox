// A local illustration. No messages are sent and no channel is created.
export function initChannelDemo(root) {
  const messages = [...root.querySelectorAll('[data-demo-message]')];
  const replay = root.querySelector('#demo-replay');
  const typing = root.querySelector('#demo-typing');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let timer;
  const finish = () => {
    clearTimeout(timer);
    messages.forEach(message => { message.hidden = false; });
    typing.hidden = true;
    replay.disabled = false;
  };
  replay.addEventListener('click', () => {
    finish();
    if (motion.matches) return;
    messages[1].hidden = true;
    typing.hidden = false;
    replay.disabled = true;
    timer = setTimeout(finish, 1800);
  });
  motion.addEventListener('change', finish);
  document.addEventListener('visibilitychange', finish);
  window.addEventListener('pagehide', finish);
  replay.hidden = false;
}
