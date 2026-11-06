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
});

