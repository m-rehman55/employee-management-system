/**
 * static/js/main.js - Interactive helpers for Employee Management System.
 */

document.addEventListener('DOMContentLoaded', function () {
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
            if (!confirm(`Are you sure you want to permanently delete ${itemName}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });

    // 3. Instant Client-Side Theme Switcher
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
        themeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const body = document.body;
            const isDark = body.classList.contains('theme-dark');
            const newTheme = isDark ? 'light' : 'dark';

            body.classList.remove('theme-light', 'theme-dark');
            body.classList.add('theme-' + newTheme);

            if (newTheme === 'dark') {
                themeBtn.innerHTML = '<i class="bi bi-sun-fill text-warning"></i> <span>Light</span>';
            } else {
                themeBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i> <span>Dark</span>';
            }

            document.cookie = `app_theme=${newTheme}; path=/; max-age=${365 * 24 * 60 * 60}; SameSite=Lax`;
            fetch(themeBtn.getAttribute('href'), { method: 'GET' }).catch(function () {});
        });
    }
});

