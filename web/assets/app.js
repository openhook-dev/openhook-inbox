import {renderSessions} from './sessions.js?v=afa9ce4d24bc';
const main = document.querySelector('#main');
const $ = selector => document.querySelector(selector);
const announce = text => { $('#announcement').textContent = text; };
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


$('#theme-toggle').hidden = false;
for (const link of document.querySelectorAll('nav a')) {
  if (link.pathname === location.pathname) link.setAttribute('aria-current', 'page');
}
for (const button of document.querySelectorAll('.copy-code')) {
  button.hidden = false;
  button.addEventListener('click', () => copy(button.previousElementSibling.textContent, button));
}
if (location.pathname === '/channels') renderSessions(main, {copy});
