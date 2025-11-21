// DTR Settings JavaScript

// Initialize settings functionality
function initSettings() {
    setupToggleHandlers();
    setupSaveSettings();
    updateSummary();
}

// Setup toggle switch handlers
function setupToggleHandlers() {
    const strictModeToggle = document.getElementById('enableStrictMode');
    const earlyInToggle = document.getElementById('allowEarlyIn');
    
    // Strict Mode toggle
    strictModeToggle.addEventListener('change', function() {
        const strictModeOptions = document.getElementById('strictModeOptions');    
        if (strictModeToggle.checked) {
            strictModeOptions.style.display = 'none';
        } else {
            strictModeOptions.style.display = 'block';
        }
    });

    // Early In toggle
    earlyInToggle.addEventListener('change', function() {
        const earlyInOptions = document.getElementById('earlyInOptions');
        if (this.checked) {
            earlyInOptions.style.display = 'block';
        } else {
            earlyInOptions.style.display = 'none';
        }
    });
}

// Validate individual input
function validateInput(input) {
    const value = input.value.trim();
    
    // Remove existing validation classes
    input.classList.remove('is-valid', 'is-invalid');
    
    // Validate based on input type
    switch(input.type) {
        case 'number':
            const min = parseInt(input.min) || 0;
            const max = parseInt(input.max) || Infinity;
            const numValue = parseInt(value);
            
            if (value === '' || isNaN(numValue) || numValue < min || numValue > max) {
                input.classList.add('is-invalid');
                return false;
            } else {
                input.classList.add('is-valid');
                return true;
            }
            
        case 'time':
            if (value === '') {
                input.classList.add('is-invalid');
                return false;
            } else {
                input.classList.add('is-valid');
                return true;
            }
            
        case 'text':
            if (input.hasAttribute('required') && value === '') {
                input.classList.add('is-invalid');
                return false;
            } else if (value !== '') {
                input.classList.add('is-valid');
                return true;
            }
            break;
    }
    
    return true;
}

function loadSettings() {
    fetch('/api/get-settings')
        .then(res => {
            if (!res.ok) throw new Error(`Server responded with ${res.status}`);
            return res.json();
        })
        .then(settings => {
            document.getElementById('unitHeadName').value = settings.unit_head || 'Not Set';
            document.getElementById('defaultStartTime').value = settings.def_start || '';
            document.getElementById('defaultEndTime').value = settings.def_end || '';
            document.getElementById('enableStrictMode').checked = settings.strict;
            document.getElementById('strictModeEndDate').value = settings.strict_duration || '';
            // document.getElementById('allowEarlyIn').checked;
            document.getElementById('earlyInMinutes').value = settings.early_allowance || '0';
            document.getElementById('allowEarlyOut').checked = settings.early;
            document.getElementById('allowOvertime').checked = settings.overtime;
            // document.getElementById('gracePeriod').value || '0';

            const strictModeOptions = document.getElementById('strictModeOptions');            
            if (settings.strict) {
                strictModeOptions.style.display = 'none';
            } else {
                strictModeOptions.style.display = 'block';
            }
            updateSummary();
        })
}

// Setup save settings functionality
function setupSaveSettings() {
    const saveButton = document.getElementById('saveSettings');
    
    saveButton.addEventListener('click', function() {
        if (validateForm()) {
            saveSettings();
        }
    });
}

// Validate entire form
function validateForm() {
    const form = document.getElementById('settingsForm');
    const inputs = form.querySelectorAll('input[type="number"], input[type="time"], input[type="text"]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    // Additional validation for time range
    const startTime = document.getElementById('defaultStartTime').value;
    const endTime = document.getElementById('defaultEndTime').value;
    
    if (startTime && endTime && startTime >= endTime) {
        document.getElementById('defaultEndTime').classList.add('is-invalid');
        isValid = false;
        showAlert('error', 'End time must be after start time');
    }
    
    return isValid;
}

// Save settings
function saveSettings() {
    const saveButton = document.getElementById('saveSettings');
    
    // Show loading state
    saveButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
    saveButton.disabled = true;

        const settings = {
            unitHeadName: document.getElementById('unitHeadName').value,
            unitHeadTitle: document.getElementById('unitHeadTitle').value,
            enableStrictMode: document.getElementById('enableStrictMode').checked,
            strictDuration: document.getElementById('strictModeEndDate').value || '',
            earlyInMinutes: document.getElementById('earlyInMinutes').value,
            allowEarlyOut: document.getElementById('allowEarlyOut').checked,
            allowOvertime: document.getElementById('allowOvertime').checked,
            defaultStartTime: document.getElementById('defaultStartTime').value,
            defaultEndTime: document.getElementById('defaultEndTime').value,
            // gracePeriod: document.getElementById('gracePeriod').value,
            // breakDuration: document.getElementById('breakDuration').value
        };
        
        setTimeout(() => {
            // Reset button state
            saveButton.innerHTML = '<i class="fas fa-save me-2"></i>Save Settings';
            saveButton.disabled = false;

            fetch('/api/update-settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', 'Settings saved successfully!');
                    console.log('Settings saved:', settings);

                    updateSummary();
                } else {
                    console.error('Error adding user:', data.error);
                }
            });
        }, 1500);
}

// Update settings summary
function updateSummary() {
    const unitHeadName = document.getElementById('unitHeadName').value || 'Not Set';
    const startTime = document.getElementById('defaultStartTime').value;
    const endTime = document.getElementById('defaultEndTime').value;
    const strictMode = document.getElementById('enableStrictMode').checked;
    const earlyIn = document.getElementById('allowEarlyIn').checked;
    const earlyInMinutes = document.getElementById('earlyInMinutes').value || '0';
    const earlyOut = document.getElementById('allowEarlyOut').checked;
    const overtime = document.getElementById('allowOvertime').checked;
    const gracePeriod = document.getElementById('gracePeriod').value || '0';
    
    // Update summary values
    document.getElementById('summaryUnitHead').textContent = unitHeadName;
    
    // Format working hours
    if (startTime && endTime) {
        const startFormatted = formatTime(startTime);
        const endFormatted = formatTime(endTime);
        document.getElementById('summaryWorkingHours').textContent = `${startFormatted} - ${endFormatted}`;
    }
    
    // Update status badges
    const strictModeStatus = document.getElementById('summaryStrictMode');
    strictModeStatus.textContent = strictMode ? 'Enabled' : 'Disabled';
    strictModeStatus.className = `status-badge ${strictMode ? 'active' : 'inactive'}`;
    
    const overtimeStatus = document.getElementById('summaryOvertime');
    overtimeStatus.textContent = overtime ? 'Allowed' : 'Disabled';
    overtimeStatus.className = `status-badge ${overtime ? 'active' : 'inactive'}`;
    
    const earlyOutStatus = document.getElementById('summaryEarlyOut');
    earlyOutStatus.textContent = earlyOut ? 'Allowed' : 'Disabled';
    earlyOutStatus.className = `status-badge ${earlyOut ? 'active' : 'inactive'}`;
    
    // Update other values
    document.getElementById('summaryEarlyIn').textContent = earlyIn ? `${earlyInMinutes} minutes` : 'Disabled';
    document.getElementById('summaryGracePeriod').textContent = `${gracePeriod} minutes`;
}

// Format time from 24h to 12h format
function formatTime(time24) {
    const [hours, minutes] = time24.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}:${minutes} ${ampm}`;
}

// Show alert messages
function showAlert(type, message) {
    const alertElement = document.getElementById('successAlert');
    
    // Update alert content and class
    alertElement.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
    alertElement.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Show alert
    alertElement.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alertElement.classList.contains('show')) {
            const alert = new bootstrap.Alert(alertElement);
            alert.close();
        }
    }, 5000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    initSettings();
});

// Handle form reset
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        document.getElementById('saveSettings').click();
    }
    
    // Escape to reset form
    if (e.key === 'Escape') {
        if (confirm('Are you sure you want to reset all changes?')) {
            document.getElementById('settingsForm').reset();
            updateSummary();
        }
    }
});