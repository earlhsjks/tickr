function initScheduleManagement() {
    loadSchedules();
    setupSearch();
    setupBrokenTimeButtons();
    setupScheduleActions();
    setupModal();
    addInteractiveEffects();
}

// Search functionality
function setupSearch() {
    const searchInput = document.getElementById('scheduleSearch');

    searchInput.addEventListener('input', function () {
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

async function loadSchedules() {
    try {
        const res = await fetch(`/api/get-schedules`);
        const data = await res.json();

        const users = data.users;
        const schedules = data.schedules;

        const userMap = {};
        users.forEach(u => {
            userMap[u.user_id] = `${u.first_name} ${u.last_name}`;
        });

        const scheduleMap = {};
        schedules.forEach(s => {
            if (!scheduleMap[s.user_id]) scheduleMap[s.user_id] = {};
            scheduleMap[s.user_id][s.day] = `${s.start_time || ''} - ${s.end_time || ''}`;
        });

        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const tbody = document.getElementById('scheduleTableBody');
        tbody.innerHTML = '';

        users.forEach(u => {
            const row = document.createElement('tr');
            let rowHTML = `
                <td class="ps-4">
                    <div class="d-flex align-items-center">
                        <div class="user-avatar me-3">${u.first_name[0]}${u.last_name[0]}</div>
                        <div>
                            <div class="user-name">${u.first_name} ${u.last_name}</div>
                            <div class="user-email">${u.user_id}</div>
                        </div>
                    </div>
                </td>
            `;

            days.forEach(day => {
                const sched = scheduleMap[u.user_id]?.[day] || '-';
                rowHTML += `<td class="text-center">${sched}</td>`;
            });

            rowHTML += `
                <td class="text-center">
                <div class="d-inline-flex gap-2 justify-content-center">
                    <button class="btn btn-sm btn-outline-primary" data-user-id="${u.user_id}" title="Edit Schedule">
                    <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" data-user-id="${u.user_id}" title="Delete">
                    <i class="fas fa-trash"></i>
                    </button>
                </div>
                </td>
            `;

            row.innerHTML = rowHTML;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error('Error loading schedules:', err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('scheduleTableBody');
    tbody.addEventListener('click', e => {
        const editBtn = e.target.closest('.btn-outline-primary');
        const deleteBtn = e.target.closest('.btn-outline-danger');

        if (editBtn) {
            const userId = editBtn.getAttribute('data-user-id');
            console.log('Edit clicked:', userId);
            
            fetch(`/api/get-schedule/${userId}`)
                .then(res => {
                    if (!res.ok) throw new Error(`Server responded with ${res.status}`);
                    return res.json();
                })
                .then(data => {
                    const user = data.user || data[0]?.user;
                    const sched = data.schedule || data[0]?.schedule || [];

                    document.getElementById('editWho').textContent = user.full_name;
                    document.getElementById('userId').value = user.user_id;

                    // Schedules IN
                    document.getElementById('mondayIn').value = sched.find(s => s.day === 'monday')?.start_time || '';
                    document.getElementById('tuesdayIn').value = sched.find(s => s.day === 'tuesday')?.start_time || '';
                    document.getElementById('wednesdayIn').value = sched.find(s => s.day === 'wednesday')?.start_time || '';
                    document.getElementById('thursdayIn').value = sched.find(s => s.day === 'thurday')?.start_time || '';
                    document.getElementById('fridayIn').value = sched.find(s => s.day === 'friday')?.start_time || '';
                    document.getElementById('saturdayIn').value = sched.find(s => s.day === 'saturday')?.start_time || '';
                    document.getElementById('sundayIn').value = sched.find(s => s.day === 'sunday')?.start_time || '';
                    
                    // Schedules OUT
                    document.getElementById('mondayOut').value = sched.find(s => s.day === 'monday')?.end_time || '';
                    document.getElementById('tuesdayOut').value = sched.find(s => s.day === 'tuesday')?.end_time || '';
                    document.getElementById('wednesdayOut').value = sched.find(s => s.day === 'wednesday')?.end_time || '';
                    document.getElementById('thursdayOut').value = sched.find(s => s.day === 'thurday')?.end_time || '';
                    document.getElementById('fridayOut').value = sched.find(s => s.day === 'friday')?.end_time || '';
                    document.getElementById('saturdayOut').value = sched.find(s => s.day === 'saturday')?.end_time || '';
                    document.getElementById('sundayIn').value = sched.find(s => s.day === 'sunday')?.end_time || '';

                    new bootstrap.Modal(document.getElementById('scheduleEditModal')).show();
                })

        }

        if (deleteBtn) {
            const userId = deleteBtn.getAttribute('data-user-id');
            console.log('Delete clicked:', userId);

            const schedules = [
                {
                    day: 'monday',
                    start_time: document.getElementById('mondayIn').value,
                    end_time: document.getElementById('mondayOut').value
                },
                {
                    day: 'tuesday',
                    start_time: document.getElementById('tuesdayIn').value,
                    end_time: document.getElementById('tuesdayOut').value
                },
                {
                    day: 'wednesday',
                    start_time: document.getElementById('wednesdayIn').value,
                    end_time: document.getElementById('wednesdayOut').value
                },
                {
                    day: 'thursday',
                    start_time: document.getElementById('thursdayIn').value,
                    end_time: document.getElementById('thursdayOut').value
                },
                {
                    day: 'friday',
                    start_time: document.getElementById('fridayIn').value,
                    end_time: document.getElementById('fridayOut').value
                },
                {
                    day: 'saturday',
                    start_time: document.getElementById('saturdayIn').value,
                    end_time: document.getElementById('saturdayOut').value
                },
            ];

            fetch(`/api/update-schedule/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userId: userId,
                    schedules: schedules
                })
            })

            const data = await res.json();
            console.log('Server response: ', data);
            if(res.ok) console.log('Schedule updated successfully!')
    });

    // SAVE SCHEDULE
    document.getElementById('saveSchedBtn').addEventListener('click', function() {
        const userId = document.getElementById('userId').value;

        console.log(userId);
    })
});

// Broken time button functionality
function setupBrokenTimeButtons() {
    const brokenTimeButtons = document.querySelectorAll('.broken-time-btn');

    brokenTimeButtons.forEach(button => {
        button.addEventListener('click', function () {
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
    clearSchedulesBtn.addEventListener('click', function () {
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

    // Add schedule button
    const addScheduleBtn = document.querySelector('.add-schedule-btn');
    addScheduleBtn.addEventListener('click', function () {
        const modal = new bootstrap.Modal(document.getElementById('scheduleEditModal'));
        modal.show();
        console.log('Add schedule modal opened');
    });

    // Edit schedule buttons
    const editButtons = document.querySelectorAll('.action-buttons .btn-outline-primary');
    editButtons.forEach(button => {
        button.addEventListener('click', function () {
            const row = this.closest('tr');
            const employeeName = row.querySelector('.user-name').textContent;

            const modal = new bootstrap.Modal(document.getElementById('scheduleEditModal'));
            modal.show();

            console.log(`Edit schedule for: ${employeeName}`);
        });
    });

    // Convert schedule buttons
    // Delete buttons
    const deleteButtons = document.querySelectorAll('.btn-outline-danger');
    deleteButtons.forEach(button => {
        if (button.title === 'Delete') {
            button.addEventListener('click', function () {
                const row = this.closest('tr');
                const employeeName = row.querySelector('.user-name').textContent;

                if (confirm(`Are you sure you want to delete the schedule for ${employeeName}?`)) {
                    console.log(`Schedule deleted for: ${employeeName}`);

                    // Visual feedback
                    row.style.opacity = '0.5';
                    setTimeout(() => {
                        row.remove();
                    }, 500);
                }
            });
        }
    });

    // Export and refresh buttons
    const exportButtons = document.querySelectorAll('.btn-outline-primary');
    exportButtons.forEach(button => {
        if (button.textContent.includes('Export')) {
            button.addEventListener('click', function () {
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
            button.addEventListener('click', function () {
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

    saveButton.addEventListener('click', function () {
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
    addBrokenScheduleBtn.addEventListener('click', function () {
        const template = brokenScheduleTemplate.cloneNode(true);
        template.id = '';
        template.classList.remove('d-none');

        // Add remove functionality
        const removeBtn = template.querySelector('.remove-broken-schedule');
        removeBtn.addEventListener('click', function () {
            template.remove();
        });

        brokenScheduleContainer.appendChild(template);
        console.log('Added new broken schedule');
    });

    // Rest day checkbox handlers
    const restDayCheckboxes = modal.querySelectorAll('[id$="Off"]');
    restDayCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
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
        row.addEventListener('mouseenter', function () {
            this.style.backgroundColor = '#f8f9fa';
        });

        row.addEventListener('mouseleave', function () {
            this.style.backgroundColor = '';
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initScheduleManagement();
});

// Keyboard shortcuts
document.addEventListener('keydown', function (e) {
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