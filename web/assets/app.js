import {animateChannel} from './channel-animation.js?v=3f399cdd2017';
import {renderSessions} from './sessions.js?v=afa9ce4d24bc';
const main = document.querySelector('#main');
const $ = selector => document.querySelector(selector);
const announce = text => { $('#announcement').textContent = text; };
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


for (const link of document.querySelectorAll('nav a')) {
  if (link.pathname === location.pathname) link.setAttribute('aria-current', 'page');
}
for (const button of document.querySelectorAll('.copy-code')) {
  button.hidden = false;
  button.addEventListener('click', () => copy(button.previousElementSibling.textContent, button));
}
if (location.pathname === '/channels') renderSessions(main, {copy});

if (location.pathname === '/') animateChannel(main);
