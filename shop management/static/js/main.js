/**
 * Main JavaScript file for Shop Management System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm delete actions
    const confirmDeleteForms = document.querySelectorAll('.confirm-delete-form');
    confirmDeleteForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });

    // Password confirmation check
    const passwordForm = document.querySelector('.password-confirm-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(event) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                event.preventDefault();
                alert('Passwords do not match!');
            }
        });
    }

    // Stock level indicator
    const stockElements = document.querySelectorAll('.stock-level');
    stockElements.forEach(function(element) {
        const stockLevel = parseInt(element.textContent);
        if (stockLevel === 0) {
            element.classList.add('text-danger', 'fw-bold');
            element.textContent += ' (Out of Stock)';
        } else if (stockLevel < 10) {
            element.classList.add('text-warning');
            element.textContent += ' (Low Stock)';
        } else {
            element.classList.add('text-success');
        }
    });

    // Search functionality for tables
    const tableSearchInputs = document.querySelectorAll('.table-search');
    tableSearchInputs.forEach(function(input) {
        input.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const tableId = this.getAttribute('data-table-id');
            const table = document.getElementById(tableId);
            
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    if (text.indexOf(searchTerm) > -1) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });

    // Dynamic form fields
    const addFieldButtons = document.querySelectorAll('.add-field-btn');
    addFieldButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const fieldContainer = document.getElementById(this.getAttribute('data-container'));
            const fieldTemplate = document.getElementById(this.getAttribute('data-template'));
            
            if (fieldContainer && fieldTemplate) {
                const newField = fieldTemplate.content.cloneNode(true);
                fieldContainer.appendChild(newField);
                
                // Add event listener to remove button
                const removeButtons = fieldContainer.querySelectorAll('.remove-field-btn');
                removeButtons.forEach(function(removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        this.closest('.dynamic-field').remove();
                    });
                });
            }
        });
    });

    // Image preview for product forms
    const imageUrlInput = document.getElementById('image_url');
    const imagePreview = document.getElementById('image-preview');
    
    if (imageUrlInput && imagePreview) {
        imageUrlInput.addEventListener('change', function() {
            const imageUrl = this.value.trim();
            if (imageUrl) {
                imagePreview.src = imageUrl;
                imagePreview.style.display = 'block';
            } else {
                imagePreview.style.display = 'none';
            }
        });
    }

    // Status change handler for tickets
    const statusSelect = document.getElementById('status');
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            const value = this.value;
            const statusBadge = document.querySelector('.status-badge');
            
            if (statusBadge) {
                // Remove existing classes
                statusBadge.classList.remove('bg-danger', 'bg-warning', 'bg-success');
                
                // Add appropriate class based on status
                if (value === 'open') {
                    statusBadge.classList.add('bg-danger');
                } else if (value === 'in-progress') {
                    statusBadge.classList.add('bg-warning');
                } else if (value === 'closed') {
                    statusBadge.classList.add('bg-success');
                }
                
                // Update text
                statusBadge.textContent = value;
            }
        });
    }

    // Dashboard charts initialization (if Chart.js is included)
    if (typeof Chart !== 'undefined') {
        // Product Categories Chart
        const ctxCategories = document.getElementById('categoriesChart');
        if (ctxCategories) {
            new Chart(ctxCategories, {
                type: 'pie',
                data: {
                    labels: ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Others'],
                    datasets: [{
                        data: [12, 19, 8, 5, 2],
                        backgroundColor: [
                            '#0d6efd',
                            '#6610f2',
                            '#6f42c1',
                            '#d63384',
                            '#fd7e14'
                        ]
                    }]
                }
            });
        }

        // Ticket Status Chart
        const ctxTickets = document.getElementById('ticketsChart');
        if (ctxTickets) {
            new Chart(ctxTickets, {
                type: 'doughnut',
                data: {
                    labels: ['Open', 'In Progress', 'Closed'],
                    datasets: [{
                        data: [5, 3, 8],
                        backgroundColor: [
                            '#dc3545',
                            '#ffc107',
                            '#198754'
                        ]
                    }]
                }
            });
        }
    }
});
