(function initMobileNav() {
  const navbar = document.querySelector(".navbar");
  const toggle = document.querySelector(".navbar__toggle");
  const menu = document.querySelector(".navbar__links");

  if (!navbar || !toggle || !menu) return;

  const overlay = document.createElement("div");
  overlay.className = "navbar__overlay";
  overlay.setAttribute("aria-hidden", "true");
  navbar.appendChild(overlay);

  function closeMenu() {
    navbar.classList.remove("navbar--open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Ouvrir le menu");
    document.body.classList.remove("menu-open");
  }

  function openMenu() {
    navbar.classList.add("navbar--open");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Fermer le menu");
    document.body.classList.add("menu-open");
  }

  toggle.addEventListener("click", () => {
    if (navbar.classList.contains("navbar--open")) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  overlay.addEventListener("click", closeMenu);

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 768) closeMenu();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMenu();
  });

  window.closeMobileMenu = closeMenu;
})();
