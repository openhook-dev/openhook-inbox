(() => {
  let theme;
  try { theme = localStorage.getItem('openhook-theme'); } catch {}
  document.documentElement.dataset.theme = ['light', 'dark'].includes(theme) ? theme : 'light';
})();
