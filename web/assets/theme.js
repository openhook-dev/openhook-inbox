(() => {
  let theme;
  try { theme = localStorage.getItem('openhook-theme'); } catch {}
  document.documentElement.dataset.theme = theme || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
})();
