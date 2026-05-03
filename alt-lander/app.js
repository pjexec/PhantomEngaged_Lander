// Scroll-reveal observer
document.addEventListener('DOMContentLoaded', () => {
  const reveals = document.querySelectorAll('.reveal');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: '0px 0px -40px 0px'
  });

  reveals.forEach(el => observer.observe(el));

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Topbar background on scroll
  const topbar = document.querySelector('.topbar');
  let ticking = false;

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        if (window.scrollY > 100) {
          topbar.style.background = 'rgba(11, 17, 32, 0.95)';
          topbar.style.borderBottomColor = 'rgba(43, 165, 165, 0.15)';
        } else {
          topbar.style.background = 'rgba(11, 17, 32, 0.85)';
          topbar.style.borderBottomColor = 'rgba(138, 155, 181, 0.12)';
        }
        ticking = false;
      });
      ticking = true;
    }
  });
});
