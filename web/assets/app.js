import {renderSessions} from './sessions.js?v=1d48b131add3';
import {registerWebMCP, setupTool} from './webmcp.js?v=bbf09139b357';
const main = document.querySelector('#main');
const $ = selector => document.querySelector(selector);
const announce = text => { $('#announcement').textContent = text; };
async function copy(text, button) {
  const original = [...button.childNodes];
  try {
    await navigator.clipboard.writeText(text);
    button.textContent = 'Copied';
    announce('Copied to clipboard.');
    setTimeout(() => { if (button.isConnected) button.replaceChildren(...original); }, 1500);
  } catch {
    button.textContent = 'Select text';
    announce('Clipboard access is unavailable. Select and copy the text.');
  }
}


for (const link of document.querySelectorAll('nav a')) {
  if (link.pathname === location.pathname) link.setAttribute('aria-current', 'page');
}
for (const button of document.querySelectorAll('.copy-code')) {
  const source = button.dataset.copyTarget
    ? document.getElementById(button.dataset.copyTarget)
    : button.previousElementSibling;
  button.hidden = false;
  button.addEventListener('click', () => copy(source.textContent, button));
}
if (location.pathname === '/channels') renderSessions(main, {copy});
else registerWebMCP(() => [setupTool()]);
