document.addEventListener("DOMContentLoaded", () => {
    // --- Elements ---
    const sidebarToggler = document.getElementById("sidebarToggler");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    const body = document.body;
    const main = document.querySelector(".main");

    if (!sidebarToggler || !sidebar) {
        console.warn("Sidebar elements missing — script aborted.");
        return;
    }

    // --- Helpers ---
    const isMobile = () => window.innerWidth <= 768;

    const closeMobileSidebar = () => {
        sidebar.classList.remove("m-open");
        overlay?.classList.remove("active");
        body.style.overflow = "";
    };

    // --- Sidebar Toggle ---
    sidebarToggler.addEventListener("click", () => {
        if (isMobile()) {
            const isOpen = sidebar.classList.toggle("m-open");
            overlay?.classList.toggle("active", isOpen);
            body.style.overflow = isOpen ? "hidden" : "";
        } else {
            sidebar.classList.toggle("collapsed");
            main?.classList.toggle("sidebar-collapsed");
        }
    });

    // --- Overlay Click (mobile) ---
    overlay?.addEventListener("click", closeMobileSidebar);

    // --- Window Resize ---
    window.addEventListener("resize", () => {
        if (!isMobile()) {
            closeMobileSidebar();
        }
    });

    // --- Active Link Detection ---
    const currentUrl = window.location.href;

    document.querySelectorAll(".sidebar-menu-item").forEach(menuItem => {
        const submenuLinks = menuItem.querySelectorAll("ul.submenu a");
        const directLinks = menuItem.querySelectorAll(":scope > a");

        const checkLink = link => {
            if (link.href === currentUrl) {
                menuItem.classList.add("open");
                link.classList.add("active");
            }
        };

        if (submenuLinks.length) {
            submenuLinks.forEach(checkLink);
        } else {
            directLinks.forEach(checkLink);
        }
    });

    // --- Submenu Toggle ---
    document.querySelectorAll(".sidebar-menu-button.has-children")
        .forEach(button => {
            button.addEventListener("click", () => {
                const parent = button.closest(".sidebar-menu-item");
                parent?.classList.toggle("open");
            });
        });
});

// Show alert messages
function showAlert(type, message) {
    // 1. Create a new alert div dynamically
    const alertElement = document.createElement('div');
    
    // 2. Add Bootstrap classes and positioning styles
    alertElement.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed shadow-sm`;
    alertElement.style.top = '20px';
    alertElement.style.right = '20px';
    alertElement.style.zIndex = '1050'; // Ensures it overlays above modals
    
    // 3. Set the HTML content inside the alert
    alertElement.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 4. Append the new alert to the page body
    document.body.appendChild(alertElement);
    
    // 5. Auto-remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(alertElement)) {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close(); // Safely removes this specific instance from the DOM
        }
    }, 5000);
}