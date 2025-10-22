document.addEventListener('DOMContentLoaded', function () {
    setupSearch();
    addInteractiveEffects();
    setupPagination();
    loadUsers();
});

async function setupSearch() {
    const searchInput = document.getElementById('userSearch');
    const tableBody = document.getElementById('usersTableBody');
    const rows = tableBody.querySelectorAll('tr');

    function filterUsers() {
        const searchTerm = searchInput.value.trim().toLowerCase();
        rows.forEach(row => {
            const rowText = row.innerText.toLowerCase();
            row.style.display = rowText.includes(searchTerm) ? '' : 'none';
        });
    }

    searchInput.addEventListener('input', function () {
        const searchTerm = this.value.trim().toLowerCase();
        filterUsers();

        if (searchTerm.length > 0) {
            this.style.borderColor = '#10b981'; // green
            setTimeout(() => {
                this.style.borderColor = '#d1d5db'; // default gray
            }, 1000);
        }
    });
}

function addInteractiveEffects() {
    document.querySelectorAll('#usersTableBody tr').forEach(row => {
        row.addEventListener('mouseenter', () => row.style.backgroundColor = '#f8f9fa');
        row.addEventListener('mouseleave', () => row.style.backgroundColor = '');
    });

    const refreshBtn = document.getElementById('refreshBtn');
    const exportBtn = document.getElementById('exportBtn');

    if (exportBtn) {
        exportBtn.addEventListener('click', function () {
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Exporting...';
            this.disabled = true;

            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-download me-1"></i>Export';
                this.disabled = false;

                const link = document.createElement('a');
                link.href = '/api/export-users';
                link.download = ''; // optional
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }, 1000);
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', async function () {
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Refreshing...';
            this.disabled = true;

            loadUsers();

            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-sync me-1"></i>Refresh';
                this.disabled = false;
            }, 2000);
        });
    }
}

function loadUsers() {
    fetch(`/api/users-data`)
        .then(res => {
            if (!res.ok) throw new Error(`Server responded with ${res.status}`);
            return res.json();
        })
        .then(users => {
            const tbody = document.getElementById('usersTableBody');
            tbody.innerHTML = '';

            users.forEach(user => {
                const tr = document.createElement('tr');

                tr.innerHTML = `
                <td class="ps-4">
                    <div class="d-flex align-items-center">
                    <div class="user-avatar me-3">
                        <div class="default-avatar rounded-circle d-flex align-items-center justify-content-center"
                            style="width: 40px; height: 40px">
                            <span class="initials">${user.first_name[0]}${user.last_name[0]}</span>
                        </div>
                    </div>
                    <div>
                        <div class="user-name">${user.first_name} ${user.last_name}</div>
                        <div class="user-email">${user.user_id}</div>
                    </div>
                    </div>
                </td>
                <td class="text-center">
                    <span class="role-badge ${user.role.toLowerCase()}">${user.role === "gia" ? "GIA" : user.role}</span>
                </td>
                <td class="text-center">
                    <span class="status-badge ${user.status.toLowerCase()}">${user.status}</span>
                </td>
                <td class="text-center">
                    <div class="last-login">
                    <div>-</div>
                    <small class="text-muted"></small>
                    </div>
                </td>
                <td class="text-center">
                    <div class="d-inline-flex gap-2 justify-content-center">
                        <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary" data-user-id="${user.user_id}" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" data-user-id="${user.user_id}" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                        </div>
                    </div>
                </td>
                `;

                tbody.appendChild(tr);
            })
        })
}

// EDIT AND DELETE
const tbody = document.getElementById('usersTableBody');
tbody.addEventListener('click', e => {
    const editBtn = e.target.closest('.btn-outline-primary');
    const deleteBtn = e.target.closest('.btn-outline-danger');

    if (editBtn) {
        const userId = editBtn.getAttribute('data-user-id');
        console.log('Edit clicked:', userId);

        fetch(`/api/get-user/${userId}`)
            .then(res => {
                if (!res.ok) throw new Error(`Server responded with ${res.status}`);
                return res.json();
            })
            .then(user => {
                document.getElementById('editUserId').value = user.user_id;
                document.getElementById('editFirstName').value = user.first_name;
                document.getElementById('editLastName').value = user.last_name;
                document.getElementById('editMiddleInitial').value = user.middle_name || '';
                document.getElementById('editRole').value = user.role_id;
                document.getElementById('editStatus').value = user.status;

                new bootstrap.Modal(document.getElementById('editUserModal')).show();
            })
            .catch(err => {
                console.error("Failed to load user:", err.message);
                alert("User not found or something went wrong.");
            });

        loadUsers();
    }

    // SUBMIT EDIT USER
    document.getElementById('saveUserChanges').addEventListener('click', function () {
        const form = document.getElementById('editUserForm');
        const userId = editBtn.getAttribute('data-user-id');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        // Show loading state
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        this.disabled = true;

        // Prepare form data
        const userData = {
            userId: document.getElementById('editUserId').value,
            firstName: document.getElementById('editFirstName').value,
            lastName: document.getElementById('editLastName').value,
            middleInitial: document.getElementById('editMiddleInitial').value,
            role: document.getElementById('editRole').value,
        };

        // Send to backend
        fetch(`/api/update-user/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        })
            .then(res => res.json())
            .then(data => {
                this.innerHTML = 'Save Changes';
                this.disabled = false;

                if (data.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editUserModal'));
                    if (modal) modal.hide();

                    loadUsers();
                    // filterUsers();

                    console.log('User updated successfully!');
                    document.getElementById('addUserForm').reset();
                } else {
                    console.error('Error updating user:', data.error);
                }
            })
            .catch(err => {
                this.innerHTML = 'Save Changes';
                this.disabled = false;
                console.error('Fetch error:', err);
            });
    });

    if (deleteBtn) {
        const userId = deleteBtn.getAttribute('data-user-id');
        console.log('Delete clicked:', userId);

        fetch(`/api/get-user/${userId}`)
            .then(res => {
                if (!res.ok) throw new Error(`Server responded with ${res.status}`);
                return res.json();
            })
            .then(user => {
                document.getElementById('deleteUserName').textContent = `${user.first_name} ${user.last_name}`;
                const modalElement = document.getElementById('deleteUserModal');
                const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
                modal.show();

                const confirmDeleteBtn = document.getElementById('confirmDeleteUser');
                confirmDeleteBtn.replaceWith(confirmDeleteBtn.cloneNode(true));
                const newConfirmBtn = document.getElementById('confirmDeleteUser');

                newConfirmBtn.addEventListener('click', function () {
                    this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Deleting...';
                    this.disabled = true;

                fetch(`/api/delete-user/${userId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userId })
                })
                    .then(async res => {
                        let data;
                        try {
                            data = await res.json();
                        } catch {
                            data = { success: false, error: 'Invalid JSON response from server' };
                        }

                        if (!res.ok || !data.success) {
                            throw new Error(data.error || `Server responded with ${res.status}`);
                        }

                        console.log('User deleted successfully');
                        modal.hide();
                        loadUsers();
                    })
                    .catch(err => {
                        console.error('Failed to delete user:', err.message);
                    })
                    .finally(() => {
                        this.innerHTML = 'Delete User';
                        this.disabled = false;
                    });
                });
            })
            .catch(err => {
                console.error("Failed to load user:", err.message);
                alert("User not found or something went wrong.");
            });
    }
});

// ADD USER MODAL
document.getElementById('saveNewUser').addEventListener('click', function () {
    const addUserForm = document.getElementById('addUserForm');

    if (!addUserForm.checkValidity()) {
        addUserForm.reportValidity();
        return;
    }

    // Gather form data
    const userData = {
        userId: document.getElementById('addUserId').value,
        firstName: document.getElementById('addFirstName').value,
        lastName: document.getElementById('addLastName').value,
        middleInitial: document.getElementById('addMiddleInitial').value || '',
        role: document.getElementById('addRole').value,
    };

    // Disable and animate button
    this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
    this.disabled = true;
    this.style.transform = 'scale(0.95)';

    // Send data to backend
    fetch('/api/add-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const modalEl = document.getElementById('addUserModal');
                const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

                // Give Bootstrap time to finish transition before hiding
                setTimeout(() => {
                    modal.hide();
                    // Remove backdrop and focus trap manually in case
                    document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    loadUsers();
                }, 300);
            } else {
                console.error('Error adding user:', data.error);
            }
        })
        .catch(err => console.error('Fetch failed:', err))
        .finally(() => {
            // Restore button after fetch finishes
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-plus me-2"></i>Add User';
                this.disabled = false;
                this.style.transform = '';
                document.getElementById('addUserForm').reset();
            }, 200);
        });
});

function setupPagination() {
    document.querySelectorAll('.pagination .page-link').forEach(link => {
        link.addEventListener('click', function (e) {
            if (!this.parentElement.classList.contains('disabled') &&
                !this.parentElement.classList.contains('active')) {
                e.preventDefault();
                document.querySelectorAll('.pagination .page-item').forEach(item => {
                    item.classList.remove('active');
                });
                this.parentElement.classList.add('active');
                console.log('Page changed to:', this.textContent);
            }
        });
    });
}

document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('userSearch').focus();
    }

    if (e.key === 'Escape') {
        const searchInput = document.getElementById('userSearch');
        if (document.activeElement === searchInput) {
            searchInput.value = '';
            filterUsers();
            searchInput.blur();
        }
    }
});
