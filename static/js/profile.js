// Profile Page JavaScript

// Initialize profile functionality
function initProfile() {
    setupPasswordToggle();
    setupPasswordStrength();
    setupSaveProfile();
    setupChangePassword();
}

function loadInfo() {
    userId = document.getElementById('userId').value;

    fetch(`/api/get-user/${userId}`)
        .then(res => {
            if (!res.ok) throw new Error(`Server responded with ${res.status}`);
            return res.json();
        })
        .then(user => {
            document.getElementById('firstName').value = user.first_name;
            document.getElementById('lastName').value = user.last_name;
            document.getElementById('middleName').value = user.middle_name || '';
            document.getElementById('fullName').innerText = `${user.first_name} ${user.last_name}`
            document.getElementById('initials').innerText = `${user.first_name[0]}${user.last_name[0]}`
        })
}

// Validate individual input
function validateInput(input) {
    const value = input.value.trim();
    
    // Remove existing validation classes
    input.classList.remove('is-valid', 'is-invalid');
    
    // Basic validation
    if (input.hasAttribute('required') && value === '') {
        input.classList.add('is-invalid');
        return false;
    }
    
    // Email validation
    if (input.type === 'email' && value !== '') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            input.classList.add('is-invalid');
            return false;
        }
    }
    
    // Username validation
    if (input.id === 'username' && value !== '') {
        const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
        if (!usernameRegex.test(value)) {
            input.classList.add('is-invalid');
            return false;
        }
    }
    
    if (value !== '') {
        input.classList.add('is-valid');
    }
    
    return true;
}

// Setup password toggle functionality
function setupPasswordToggle() {
    const toggleButtons = [
        { button: 'toggleCurrentPassword', input: 'currentPassword' },
        { button: 'toggleNewPassword', input: 'newPassword' },
        { button: 'toggleConfirmPassword', input: 'confirmPassword' }
    ];
    
    toggleButtons.forEach(({ button, input }) => {
        const toggleBtn = document.getElementById(button);
        const inputField = document.getElementById(input);
        
        if (toggleBtn && inputField) {
            toggleBtn.addEventListener('click', function() {
                const type = inputField.getAttribute('type') === 'password' ? 'text' : 'password';
                inputField.setAttribute('type', type);
                
                const icon = this.querySelector('i');
                icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
            });
        }
    });
}

// Setup password strength indicator
function setupPasswordStrength() {
    const newPasswordInput = document.getElementById('newPassword');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const strengthIndicator = document.getElementById('passwordStrength');
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    
    newPasswordInput.addEventListener('input', function() {
        const password = this.value;
        
        if (password.length > 0) {
            strengthIndicator.style.display = 'block';
            const strength = calculatePasswordStrength(password);
            updateStrengthIndicator(strength, strengthBar, strengthText);
        } else {
            strengthIndicator.style.display = 'none';
        }
        
        // Validate confirm password if it has value
        if (confirmPasswordInput.value) {
            validatePasswordMatch();
        }
    });
    
    confirmPasswordInput.addEventListener('input', validatePasswordMatch);
}

// Calculate password strength
function calculatePasswordStrength(password) {
    let score = 0;
    
    // Length check
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    
    // Character variety checks
    if (/[a-z]/.test(password)) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    return Math.min(score, 4);
}

// Update strength indicator
function updateStrengthIndicator(strength, bar, text) {
    const colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745'];
    const labels = ['Very Weak', 'Weak', 'Fair', 'Strong'];
    const widths = [25, 50, 75, 100];
    
    const color = colors[Math.min(strength, 3)];
    const label = labels[Math.min(strength, 3)];
    const width = widths[Math.min(strength, 3)];
    
    bar.style.backgroundColor = color;
    bar.style.width = width + '%';
    text.textContent = label;
    text.style.color = color;
}

// Validate password match
function validatePasswordMatch() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const confirmInput = document.getElementById('confirmPassword');
    
    confirmInput.classList.remove('is-valid', 'is-invalid');
    
    if (confirmPassword === '') {
        return;
    }
    
    if (newPassword === confirmPassword) {
        confirmInput.classList.add('is-valid');
        return true;
    } else {
        confirmInput.classList.add('is-invalid');
        return false;
    }
}

// Setup save profile functionality
function setupSaveProfile() {
    const saveButton = document.getElementById('saveProfile');
    
    saveButton.addEventListener('click', function() {
        if (validateProfileForm()) {
            saveProfile();
        }
    });
}

// Validate profile form
function validateProfileForm() {
    const form = document.getElementById('profileForm');
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function saveProfile() {
    const btn = document.getElementById('saveProfile');

    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
    btn.disabled = true;

    const profileData = {
        username: document.getElementById('username').value,
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        middleName: document.getElementById('middleName').value
        // email: document.getElementById('email').value,
        // phone: document.getElementById('phone').value
    };

    fetch('/api/update-profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
    })
    .then(res => res.json())
    .then(data => {
        btn.innerHTML = '<i class="fas fa-save me-2"></i>Save Changes';
        btn.disabled = false;

        if (!data.success) {
            showAlert('danger', data.error || "Something went wrong");
            return;
        }

        loadInfo();
        showAlert('success', 'Profile updated successfully!');
        console.log('Profile saved:', data.updated);
    })
    .catch(err => {
        btn.innerHTML = '<i class="fas fa-save me-2"></i>Save Changes';
        btn.disabled = false;
        showAlert('danger', 'Network error, try again.');
        console.log(err);
    });
}

// Setup change password functionality
function setupChangePassword() {
    const changePasswordBtn = document.getElementById('changePassword');
    
    changePasswordBtn.addEventListener('click', function() {
        if (validatePasswordForm()) {
            changePassword();
        }
    });
}

// Validate password form
function validatePasswordForm() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Check if all fields are filled
    if (!currentPassword || !newPassword || !confirmPassword) {
        showAlert('error', 'Please fill in all password fields.');
        return false;
    }
    
    // Check password length
    if (newPassword.length < 8) {
        showAlert('error', 'New password must be at least 8 characters long.');
        return false;
    }
    
    // Check password match
    if (!validatePasswordMatch()) {
        showAlert('error', 'New passwords do not match.');
        return false;
    }
    
    return true;
}

function changePassword() {
    const btn = document.getElementById('changePassword');
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Changing...';
    btn.disabled = true;

    fetch('/api/change-password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            currentPassword,
            newPassword,
            confirmPassword
        })
    })
    .then(res => res.json())
    .then(data => {
        btn.innerHTML = '<i class="fas fa-key me-2"></i>Change Password';
        btn.disabled = false;

        if (!data.success) {
            showAlert('danger', data.error || "Something went wrong");
            return;
        }

        // Clear fields
        document.getElementById('currentPassword').value = '';
        document.getElementById('newPassword').value = '';
        document.getElementById('confirmPassword').value = '';
        document.getElementById('passwordStrength').style.display = 'none';

        const inputs = document.querySelectorAll('#passwordForm input');
        inputs.forEach(i => i.classList.remove('is-valid', 'is-invalid'));

        showAlert('success', 'Password changed successfully!');
    })
    .catch(err => {
        btn.innerHTML = '<i class="fas fa-key me-2"></i>Change Password';
        btn.disabled = false;
        showAlert('danger', 'Network error, try again.');
        console.log(err);
    });
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
    initProfile();
    loadInfo();
});

// Handle keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save profile
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        document.getElementById('saveProfile').click();
    }
    
    // Escape to clear form focus
    if (e.key === 'Escape') {
        document.activeElement.blur();
    }
});