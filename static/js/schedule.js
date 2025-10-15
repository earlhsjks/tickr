// GIA Schedule Management JavaScript

const { createElement } = require("react");

// Initialize schedule management functionality
function initScheduleManagement() {
    setupSearch();
    setupBrokenTimeButtons();
    setupScheduleActions();
    setupModal();
    addInteractiveEffects();
}

// Search functionality
function setupSearch() {
    const searchInput = document.getElementById('scheduleSearch');
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.trim().toLowerCase();
        filterSchedules();
        
        // Visual feedback
        if (searchTerm.length > 0) {
            this.style.borderColor = '#10b981';
            setTimeout(() => {
                this.style.borderColor = '#d1d5db';
            }, 1000);
        }
    });
}

function loadSchedules() {
    fetch(`/api/schedule-data`)
    .then(res => {
        if (!res.ok) throw new Error(`Server responded with ${res.status}`);
        return res.json();
    })
    .then(users => {
        const tbody = document.getElementById('scheduleTableBody');
        tbody.innerHTML = '';

        users.forEach(user => {
            const tr = createElement('tr');

            tr.innerHTML = `
            <td class="ps-4">
                <div class="d-flex align-items-center">
                    <div class="user-avatar me-3">JS</div>
                    <div>
                        <div class="user-name">John Smith</div>
                        <!-- <div class="user-email">Engineering Manager</div> -->
                    </div>
                </div>
            </td>
            <td>
                <div class="schedule-time">
                    <div class="time-display">8:00-5:00</div>
                    <small class="text-muted">8 hours</small>
                </div>
            </td>
            <td>
                <div class="schedule-time">
                    <div class="time-display">8:00-5:00</div>
                    <small class="text-muted">8 hours</small>
                </div>
            </td>
            <td>
                <div class="schedule-time">
                    <div class="time-display">8:00-5:00</div>
                    <small class="text-muted">8 hours</small>
                </div>
            </td>
            <td>
                <div class="schedule-time">
                    <div class="time-display">8:00-5:00</div>
                    <small class="text-muted">8 hours</small>
                </div>
            </td>
            <td>
                <div class="schedule-time">
                    <div class="time-display">8:00-5:00</div>
                    <small class="text-muted">8 hours</small>
                </div>
            </td>
            <td>
                <div class="schedule-time">
                    <div class="time-display">Off</div>
                    <small class="text-muted">Rest day</small>
                </div>
            </td>
            <td>
                <div class="schedule-time">
                    <div class="time-display">Off</div>
                    <small class="text-muted">Rest day</small>
                </div>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-outline-primary" title="Edit Schedule">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
            `;
        })
    })
}

// Broken time button functionality
function setupBrokenTimeButtons() {
    const brokenTimeButtons = document.querySelectorAll('.broken-time-btn');
    
    brokenTimeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const isBroken = this.getAttribute('data-broken') === 'true';
            
            if (isBroken) {
                // Switch to normal time
                this.setAttribute('data-broken', 'false');
                this.className = 'btn btn-sm btn-outline-warning broken-time-btn';
                this.innerHTML = '<i class="fas fa-play me-1"></i>Normal Time';
                
                // Get employee name for feedback
                const row = this.closest('tr');
                const employeeName = row.querySelector('.user-name').textContent;
                console.log(`${employeeName} switched to normal time`);
                
            } else {
                // Switch to broken time
                this.setAttribute('data-broken', 'true');
                this.className = 'btn btn-sm btn-warning broken-time-btn active';
                this.innerHTML = '<i class="fas fa-pause me-1"></i>Broken Time';
                
                // Get employee name for feedback
                const row = this.closest('tr');
                const employeeName = row.querySelector('.user-name').textContent;
                console.log(`${employeeName} switched to broken time`);
            }
            
            // Visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
}

// Schedule action buttons
function setupScheduleActions() {
    // Clear all schedules button
    const clearSchedulesBtn = document.querySelector('.clear-schedules-btn');
    clearSchedulesBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear all schedules? This action cannot be undone.')) {
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Clearing...';
            this.disabled = true;
            
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-broom me-2"></i>Clear All Schedules';
                this.disabled = false;
                console.log('All schedules cleared');
            }, 2000);
        }
    });
    
    // Edit schedule buttons
    const editButtons = document.querySelectorAll('.action-buttons .btn-outline-primary');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const employeeName = row.querySelector('.user-name').textContent;
            
            const modal = new bootstrap.Modal(document.getElementById('scheduleEditModal'));
            modal.show();
            
            console.log(`Edit schedule for: ${employeeName}`);
        });
    });
    
    // Export and refresh buttons
    const exportButtons = document.querySelectorAll('.btn-outline-primary');
    exportButtons.forEach(button => {
        if (button.textContent.includes('Export')) {
            button.addEventListener('click', function() {
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Exporting...';
                this.disabled = true;
                
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-download me-1"></i>Export';
                    this.disabled = false;
                }, 2000);
            });
        }
    });
    
    const refreshButtons = document.querySelectorAll('.btn-outline-secondary');
    refreshButtons.forEach(button => {
        if (button.textContent.includes('Refresh')) {
            button.addEventListener('click', function() {
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Refreshing...';
                this.disabled = true;
                
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-sync me-1"></i>Refresh';
                    this.disabled = false;
                }, 1500);
            });
        }
    });
}

// Modal functionality
function setupModal() {
    const modal = document.getElementById('scheduleEditModal');
    const form = document.getElementById('scheduleEditForm');
    const saveButton = modal.querySelector('.btn-primary');
    const addBrokenScheduleBtn = document.getElementById('addBrokenSchedule');
    const brokenScheduleContainer = document.getElementById('brokenScheduleContainer');
    const brokenScheduleTemplate = document.getElementById('brokenScheduleTemplate');
    
    saveButton.addEventListener('click', function() {
        const formData = new FormData(form);
        console.log('Saving schedule changes...');
        
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        this.disabled = true;
        
        setTimeout(() => {
            this.innerHTML = 'Save Changes';
            this.disabled = false;
            
            const modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();
            
            console.log('Schedule saved successfully');
        }, 1500);
    });
    
    // Add broken schedule functionality
    addBrokenScheduleBtn.addEventListener('click', function() {
        const template = brokenScheduleTemplate.cloneNode(true);
        template.id = '';
        template.classList.remove('d-none');
        
        // Add remove functionality
        const removeBtn = template.querySelector('.remove-broken-schedule');
        removeBtn.addEventListener('click', function() {
            template.remove();
        });
        
        brokenScheduleContainer.appendChild(template);
        console.log('Added new broken schedule');
    });
    
    // Rest day checkbox handlers
    const restDayCheckboxes = modal.querySelectorAll('[id$="Off"]');
    restDayCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const day = this.id.replace('Off', '');
            const timeInputs = modal.querySelectorAll(`#${day}In, #${day}Out`);
            
            timeInputs.forEach(input => {
                input.disabled = this.checked;
                if (this.checked) {
                    input.value = '';
                }
            });
        });
    });
}

// Filter schedules based on search
function filterSchedules() {
    const searchTerm = document.getElementById('scheduleSearch').value.toLowerCase();
    const tableBody = document.getElementById('scheduleTableBody');
    
    const rows = tableBody.querySelectorAll('tr');
    let visibleCount = 0;
    
    rows.forEach(row => {
        const employeeName = row.querySelector('.user-name').textContent.toLowerCase();
        const department = row.querySelector('.department-badge').textContent.toLowerCase();
        
        const matchesSearch = employeeName.includes(searchTerm) || department.includes(searchTerm);
        
        if (matchesSearch) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    console.log(`Showing ${visibleCount} schedules`);
}

// Add interactive effects
function addInteractiveEffects() {
    // Table row hover effects
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initScheduleManagement();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('scheduleSearch').focus();
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('scheduleSearch');
        if (document.activeElement === searchInput) {
            searchInput.value = '';
            filterSchedules();
            searchInput.blur();
        }
    }
    
});