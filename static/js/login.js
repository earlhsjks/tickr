document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch('/auth/whoami');
        const data = await res.json();

        if (data.loggedIn) {
            if (data.role === 'gia') window.location.href = '/dashboard';
            if (data.role === 'admin' || data.role === 'superadmin') window.location.href = '/admin/dashboard';
        }
    } catch (err) {
        console.error("Auth check failed: ", err);
    }
})

// Dynamic Form Switch
const toggleLink = document.getElementById('toggleLink');
const toggleText = document.getElementById('toggleText');
const loginTitle = document.getElementById('loginTitle');
const employeeForm = document.getElementById('employeeForm');
const adminForm = document.getElementById('adminForm');
const giaInput = document.getElementById('giaId');
const adminInput = document.getElementById('adminId');

toggleLink.addEventListener('click', (e) => {
    e.preventDefault();
    const isEmployee = employeeForm.classList.contains('d-none');
    
    if (isEmployee) {
    // Switch to Employee Login
    adminForm.classList.add('d-none');
    employeeForm.classList.remove('d-none');
    loginTitle.textContent = "Computer Center DTR System";
    toggleLink.textContent = "Login as Admin";
    toggleText.textContent = "Admin?";
    giaInput.focus();

    } else {
    // Switch to Admin Login
    employeeForm.classList.add('d-none');
    adminForm.classList.remove('d-none');
    loginTitle.textContent = "Admin Login";
    toggleLink.textContent = "Login as GIA";
    toggleText.textContent = "Employee?";
    adminInput.focus();
    }
});

document.getElementById('employeeForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const giaId = document.getElementById('giaId').value;

    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ giaId }),
        })

        const data = await res.json();

        if (!res.ok) {
            console.log(data.error || 'Login failed!');
            return;
        }

        console.log(data.message);
        window.location.href = '/dashboard'
    } catch (err) {
        console.error('Login error: ', err);
        console.error("Something went wrong.")
    }
})


document.getElementById('adminForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const adminId = document.getElementById('adminId').value.trim();
    const password = document.getElementById('adminPassword').value;

    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ adminId, password }),
        });

        const data = await res.json();

        if (!res.ok) {
            console.warn(data.error || 'Login failed!');
            alert(data.error || 'Invalid ID or password.');
            return;
        }

        console.log(data.message || 'Login successful');
        window.location.href = '/admin/dashboard';
    } catch (err) {
        console.error('Login error:', err);
        alert('Something went wrong. Please try again later.');
    }
});