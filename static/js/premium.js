/* ============================================================
   PM Internship — Premium Interactions
   Adds scroll reveal + counter animation on top of main.js
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initScrollReveal();
  initCounterAnimation();
  initNavbarScroll();
  document.body.classList.add('page-transition');
});

/* ==================== SCROLL REVEAL ==================== */
function initScrollReveal() {
  const els = document.querySelectorAll('.animate-on-scroll');
  if (!els.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .05, rootMargin: '0px 0px -20px 0px' });

  els.forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      el.classList.add('visible');
    } else {
      observer.observe(el);
    }
  });
}

/* ==================== COUNTER ANIMATION ==================== */
function initCounterAnimation() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .5 });

  document.querySelectorAll('.stat-number').forEach(el => observer.observe(el));
}

function animateCounter(el) {
  const text = el.textContent;
  const hasPercent = text.includes('%');
  const val = parseFloat(text.replace(/[^0-9.]/g, ''));
  if (isNaN(val)) return;

  const duration = 1800;
  const start = performance.now();

  function tick(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - (1 - progress) * (1 - progress);
    const current = val * eased;

    el.textContent = hasPercent
      ? `${current.toFixed(1)}%`
      : Number.isInteger(val) ? Math.floor(current) : current.toFixed(1);

    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/* ==================== NAVBAR SCROLL ==================== */
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
        ticking = false;
      });
      ticking = true;
    }
  });
}
