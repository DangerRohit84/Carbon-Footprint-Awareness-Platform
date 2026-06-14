(function () {
  'use strict';

  var navToggle = document.getElementById('nav-toggle');
  var navLinks = document.getElementById('nav-links');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      var expanded = navToggle.getAttribute('aria-expanded') !== 'true';
      navToggle.setAttribute('aria-expanded', expanded);
      navLinks.classList.toggle('active');
    });

    document.addEventListener('click', function (e) {
      if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('active');
      }
    });

    var links = navLinks.querySelectorAll('a');
    links.forEach(function (link) {
      link.addEventListener('click', function () {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('active');
      });
    });
  }

  var form = document.getElementById('footprint-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      var requiredFields = form.querySelectorAll('[required]');
      var valid = true;
      var firstInvalid = null;

      requiredFields.forEach(function (field) {
        if (!field.value) {
          field.style.borderColor = '#d32f2f';
          valid = false;
          if (!firstInvalid) firstInvalid = field;
        } else {
          field.style.borderColor = '';
        }
      });

      if (!valid && firstInvalid) {
        e.preventDefault();
        firstInvalid.focus();
        var errorContainer = form.querySelector('.error-summary');
        if (!errorContainer) {
          var summary = document.createElement('div');
          summary.className = 'error-summary';
          summary.setAttribute('role', 'alert');
          summary.innerHTML = '<ul><li>Please fill in all required fields.</li></ul>';
          form.insertBefore(summary, form.firstChild);
        }
      }
    });
  }
})();
