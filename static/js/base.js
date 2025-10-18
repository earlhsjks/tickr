document.addEventListener("DOMContentLoaded", function () {
    const sidebarToggler = document.getElementById('sidebarToggler');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const body = document.body;

    if (!sidebarToggler || !sidebar) {
        console.warn("Sidebar elements missing — script aborted.");
        return;
    }

    function isMobile() {
        return window.innerWidth <= 768;
    }

    sidebarToggler.addEventListener('click', () => {
        if (isMobile()) {
            // --- Mobile behavior ---
            const isNowOpen = sidebar.classList.toggle('m-open');
            overlay?.classList.toggle('active', isNowOpen);
            body.style.overflow = isNowOpen ? 'hidden' : '';
        } else {
            // --- Desktop behavior with smooth push animation ---
            sidebar.classList.toggle('collapsed');
            document.querySelector('.main')?.classList.toggle('sidebar-collapsed');
        }
    });

    overlay?.addEventListener('click', () => {
        sidebar.classList.remove('m-open');
        overlay.classList.remove('active');
        body.style.overflow = ''; // Restore scrolling
    });

    window.addEventListener('resize', () => {
        if (!isMobile()) {
            // Reset mobile-only states
            sidebar.classList.remove('m-open');
            overlay?.classList.remove('active');
            body.style.overflow = '';
        }
    });

    // --- Sidebar link activation ---
    const currentUrl = window.location.href;
    document.querySelectorAll(".sidebar-menu-item").forEach(menuItem => {
        const submenuLinks = menuItem.querySelectorAll("ul.submenu a");
        const directLinks = menuItem.querySelectorAll(":scope > a"); // only direct links

        if (submenuLinks.length > 0) {
            submenuLinks.forEach(link => {
                if (link.href === currentUrl) {
                    menuItem.classList.add("open");
                    link.classList.add("active");
                }
            });
        } else {
            directLinks.forEach(link => {
                if (link.href === currentUrl) {
                    menuItem.classList.add("open");
                    link.classList.add("active");
                }
            });
        }
    });

    // --- Dropdown toggle for submenus ---
    document.querySelectorAll(".sidebar-menu-button.has-children").forEach(button => {
        button.addEventListener("click", function () {
            const parentLi = this.closest(".sidebar-menu-item");
            parentLi.classList.toggle("open");
        });
    });
});


sidebarToggler.addEventListener('click', () => {
    if (isMobile()) {
        // Mobile behavior
        const isNowOpen = sidebar.classList.toggle('m-open');
        overlay.classList.toggle('active', isNowOpen);
        body.style.overflow = isNowOpen ? 'hidden' : '';
    } else {
        // Desktop behavior with smooth push animation
        sidebar.classList.toggle('collapsed');
        document.querySelector('.main').classList.toggle('sidebar-collapsed');
    }
});

const sidebarToggler = document.getElementById('sidebarToggler');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const body = document.body;

function isMobile() {
    return window.innerWidth <= 768;
}

sidebarToggler.addEventListener('click', () => {
    if (isMobile()) {
        // Mobile behavior
        const isNowOpen = sidebar.classList.toggle('m-open');
        overlay.classList.toggle('active', isNowOpen);
        body.style.overflow = isNowOpen ? 'hidden' : '';
    } else {
        // Desktop behavior with smooth push animation
        sidebar.classList.toggle('collapsed');
        document.querySelector('.main').classList.toggle('sidebar-collapsed');
    }
});

overlay.addEventListener('click', () => {
    sidebar.classList.remove('m-open');
    overlay.classList.remove('active');
    body.style.overflow = ''; // Restore scrolling when overlay is closed
});

window.addEventListener('resize', () => {
    if (!isMobile()) {
        // Reset mobile-specific states when resizing to desktop
        // sidebar.classList.remove('m-open');
        // overlay.classList.remove('active');
        body.style.overflow = '';
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const currentUrl = window.location.href;

    // Loop through all sidebar menu items that have submenus
    document.querySelectorAll(".sidebar-menu-item").forEach(menuItem => {
        const submenuLinks = menuItem.querySelectorAll("ul.submenu a");

        if (submenuLinks.length === 0) {
            const pMenu = menuItem.querySelectorAll("a");

            pMenu.forEach(link => {
                if (link.href === currentUrl) {
                    // Add active/open classes to parent
                    menuItem.classList.add("open");
                    // Optionally highlight the active child link
                    link.classList.add("active");
                }
            });
        }

        submenuLinks.forEach(link => {
            if (link.href === currentUrl) {
                // Add active/open classes to parent
                menuItem.classList.add("open");

                // Optionally highlight the active child link
                link.classList.add("active");
            }
        });
    });

    // Handle click toggles
    document.querySelectorAll(".sidebar-menu-button.has-children").forEach(button => {
        button.addEventListener("click", function () {
            const parentLi = this.closest(".sidebar-menu-item");
            parentLi.classList.toggle("open");
        });
    });
});