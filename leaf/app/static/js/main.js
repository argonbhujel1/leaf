/**
 * Leafletang Enterprises — Public Site JS
 * Minimal vanilla JS for navigation, lightbox, lazy loading
 */
(function () {
  'use strict';

  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav-main');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
      toggle.classList.toggle('active');
      document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
    });
    // Close on link click
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.classList.remove('active');
        document.body.style.overflow = '';
      });
    });
  }

  // Lightbox for gallery
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox ? lightbox.querySelector('img') : null;
  const lightboxClose = lightbox ? lightbox.querySelector('.lightbox-close') : null;

  document.querySelectorAll('[data-lightbox]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      if (!lightbox || !lightboxImg) return;
      const src = el.getAttribute('data-lightbox') || el.querySelector('img')?.src;
      const alt = el.getAttribute('data-alt') || el.querySelector('img')?.alt || '';
      if (src) {
        lightboxImg.src = src;
        lightboxImg.alt = alt;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  if (lightboxClose) {
    lightboxClose.addEventListener('click', closeLightbox);
  }
  if (lightbox) {
    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) closeLightbox();
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeLightbox();
  });

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
  }

  // Lazy loading fallback for older browsers
  if ('loading' in HTMLImageElement.prototype === false) {
    document.querySelectorAll('img[loading="lazy"]').forEach(function (img) {
      if (img.dataset.src) {
        img.src = img.dataset.src;
      }
    });
  }

  // Active nav highlight
  const path = window.location.pathname;
  document.querySelectorAll('.nav-main a').forEach(function (link) {
    const href = link.getAttribute('href');
    if (href === path || (href !== '/' && path.startsWith(href))) {
      link.classList.add('active');
    }
  });
})();
