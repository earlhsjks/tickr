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
