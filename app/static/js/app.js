/**
 * EcoTrack client-side functionality.
 * - Responsive navigation toggle
 * - Client-side form validation before submission
 * All in strict mode and wrapped in an IIFE to avoid global scope pollution.
 */
(function () {
  'use strict';

  /* -------- Mobile navigation toggle -------- */
  var navToggle = document.getElementById('nav-toggle');
  var navLinks = document.getElementById('nav-links');

  if (navToggle && navLinks) {
    // Toggle the menu open / closed on button click.
    navToggle.addEventListener('click', function () {
      var expanded = navToggle.getAttribute('aria-expanded') !== 'true';
      navToggle.setAttribute('aria-expanded', expanded);
      navLinks.classList.toggle('active');
    });

    // Close the menu when clicking outside of it.
    document.addEventListener('click', function (e) {
      if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('active');
      }
    });

    // Close the menu when a nav link is clicked (single-page feel).
    var links = navLinks.querySelectorAll('a');
    links.forEach(function (link) {
      link.addEventListener('click', function () {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('active');
      });
    });
  }

  /* -------- Client-side form validation -------- */
  var form = document.getElementById('footprint-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      var requiredFields = form.querySelectorAll('[required]');
      var valid = true;
      var firstInvalid = null;

      // Reset all aria-invalid states first.
      requiredFields.forEach(function (field) {
        field.setAttribute('aria-invalid', 'false');
        field.style.borderColor = '';
      });

      // Check every required field has a value.
      requiredFields.forEach(function (field) {
        if (!field.value) {
          field.setAttribute('aria-invalid', 'true');
          field.style.borderColor = '#d32f2f';
          valid = false;
          if (!firstInvalid) firstInvalid = field;
        }
      });

      // If any field is invalid, prevent submission and create error summary.
      if (!valid && firstInvalid) {
        e.preventDefault();
        firstInvalid.focus();

        var errorContainer = form.querySelector('.error-summary');
        if (!errorContainer) {
          var summary = document.createElement('div');
          summary.className = 'error-summary';
          summary.setAttribute('role', 'alert');
          summary.setAttribute('aria-labelledby', 'client-error-heading');
          summary.innerHTML = '<h2 id="client-error-heading" class="sr-only">Form Errors</h2><ul><li>Please fill in all required fields.</li></ul>';
          form.insertBefore(summary, form.firstChild);
        }
      }
    });
  }
})();
