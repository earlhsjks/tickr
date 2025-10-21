// Dynamic Form Switch
const toggleLink = document.getElementById('toggleLink');
const toggleText = document.getElementById('toggleText');
const loginTitle = document.getElementById('loginTitle');
const employeeForm = document.getElementById('employeeForm');
const adminForm = document.getElementById('adminForm');
const giaInput = document.getElementById('giaId');
const giaError = document.getElementById('giaError');
const adminInput = document.getElementById('adminId');
const adminPass = document.getElementById('adminPassword');
const adminError = document.getElementById('adminError');

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
    toggleText.textContent = "GIA?";
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
            // console.log(data.error || 'Login failed!');
            giaInput.style.border = '1px solid #dc3545'
            giaError.textContent = 'No account found with that ID.'
            return;
        }

        console.log(data.message);
        window.location.href = '/dashboard'
    } catch (err) {
        // console.error('Login error: ', err);
        // console.error("Something went wrong.")
        giaError.textContent = 'No account found with that ID.'
    }
})

giaInput.addEventListener('input', () => {
    giaInput.style.border = '';
    giaError.textContent = '';
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
            // console.warn(data.error || 'Login failed!');
            // alert(data.error || 'Invalid ID or password.');
            adminInput.style.border = '1px solid #dc3545'
            adminPass.style.border = '1px solid #dc3545'
            adminError.textContent = 'Incorrect username or password.'
            changed.user = false;
            changed.pass = false;
            return;
        }

        // console.log(data.message || 'Login successful');
        window.location.href = '/admin/dashboard';
    } catch (err) {
        console.error('Login error:', err);
    }
});

function isChange() {
    if (changed.user === true && changed.pass === true)
        adminError.textContent = '';
}

let changed = {
    user: false,
    pass: false
}

adminInput.addEventListener('input', () => {
    adminInput.style.border = '';
    changed.user = true;
    isChange();
})

adminPass.addEventListener('input', () => {
    adminPass.style.border = '';
    changed.pass = true;
    isChange();
})