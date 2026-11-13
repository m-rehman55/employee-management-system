/**
 * static/js/main.js - Interactive helpers for Employee Management System.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Add the server-issued CSRF token to every same-origin state-changing form.
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        document.querySelectorAll('form').forEach(function (form) {
            const method = (form.getAttribute('method') || 'GET').toUpperCase();
            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && !form.querySelector('[name="_csrf_token"]')) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = '_csrf_token';
                input.value = csrfMeta.content;
                form.appendChild(input);
            }
        });
    }

    // 1. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Safe Delete Confirmation Handler
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            const itemName = button.getAttribute('data-item-name') || 'this record';
            const message = button.getAttribute('data-confirm-message') ||
                `Are you sure you want to permanently delete ${itemName}? This action cannot be undone.`;
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 3. Theme system: follow OS preference until the user chooses an override.
    const themeBtn = document.getElementById('theme-toggle-btn');
    const body = document.body;
    const systemTheme = window.matchMedia
        ? window.matchMedia('(prefers-color-scheme: dark)')
        : null;

    function systemIsDark() {
        return systemTheme ? systemTheme.matches : false;
    }

    function effectiveDark() {
        return body.classList.contains('theme-dark') ||
            (body.classList.contains('theme-auto') && systemIsDark());
    }

    function updateThemeButton() {
        if (!themeBtn) {
            return;
        }
        const dark = effectiveDark();
        themeBtn.innerHTML = dark
            ? '<i class="bi bi-sun-fill text-warning"></i> <span>Light</span>'
            : '<i class="bi bi-moon-stars-fill"></i> <span>Dark</span>';
        themeBtn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    }

    if (themeBtn) {
        updateThemeButton();
        themeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const newTheme = effectiveDark() ? 'light' : 'dark';

            body.classList.remove('theme-auto', 'theme-light', 'theme-dark');
            body.classList.add('theme-' + newTheme);
            document.cookie = 'app_theme=' + newTheme + '; path=/; max-age=' +
                (365 * 24 * 60 * 60) + '; SameSite=Lax';
            updateThemeButton();
        });
    }

    if (systemTheme && systemTheme.addEventListener) {
        systemTheme.addEventListener('change', function (event) {
            if (body.classList.contains('theme-auto')) {
                body.classList.toggle('theme-dark', event.matches);
                updateThemeButton();
            }
        });
    }
});

