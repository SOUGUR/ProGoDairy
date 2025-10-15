  document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('recent-pages-toggle');
  const list = document.getElementById('recent-pages-list');

  if (!toggle || !list) return; 

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    list.style.display = list.style.display === 'block' ? 'none' : 'block';
  });

  document.addEventListener('click', (e) => {
    if (!list.contains(e.target) && e.target !== toggle) {
      list.style.display = 'none';
    }
  });
});