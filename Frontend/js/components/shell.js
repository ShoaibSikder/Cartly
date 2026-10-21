import { signOut } from "../api/account-api.js?v=cartly-auth-20261021";
import { friendlyErrorMessage } from "../api/api-client.js?v=cartly-auth-csrf-20261021";
import { assetUrl, pageUrl } from "../config.js?v=cartly-account-sidebar-20261021";

const homeIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m3 11.5 9-7.5 9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>';
const shopIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>';
const userIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/></svg>';
const heartIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20.8 8.8c0 5.4-8.8 11-8.8 11s-8.8-5.6-8.8-11a4.8 4.8 0 0 1 8.8-2.5 4.8 4.8 0 0 1 8.8 2.5Z"/></svg>';
const cartIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.7 12.2a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 8H6.2"/></svg>';
const developerSocialLinks = [
  { label: "Portfolio", href: "https://shoaibsikderportfolio.vercel.app", icon: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>' },
  { label: "Facebook", href: "https://www.facebook.com/shoaib.sikder.35", icon: '<path d="M14 8h3V4h-3a5 5 0 0 0-5 5v2H6v4h3v5h4v-5h3l1-4h-4V9a1 1 0 0 1 1-1Z"/>' },
  { label: "LinkedIn", href: "https://www.linkedin.com/in/md-shoaib-sikder-232abb3b3/", icon: '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 10v6M8 7.5v.1M12 16v-6m0 3a3 3 0 0 1 6 0v3"/>' },
  { label: "GitHub", href: "https://github.com/ShoaibSikder", icon: '<path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 6v-3.9a3.4 3.4 0 0 0-.9-2.7c3-.3 6.1-1.5 6.1-6.7a5.2 5.2 0 0 0-1.4-3.6 4.8 4.8 0 0 0-.1-3.6S17.5 1.2 15 3a13 13 0 0 0-7 0C5.5 1.2 4.3 1.5 4.3 1.5a4.8 4.8 0 0 0-.1 3.6 5.2 5.2 0 0 0-1.4 3.6c0 5.2 3.1 6.4 6.1 6.7A3.4 3.4 0 0 0 8 18v4"/>' },
];

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

function badge(count) {
  return `<span class="count-badge"${count ? "" : " hidden"} aria-hidden="true">${count || ""}</span>`;
}

export function renderShell(user, cartCount, pageName, wishlistCount = 0) {
  const signedIn = Boolean(user);
  const activeShop = pageName === "products" || pageName === "product" || pageName === "reviews";
  const accountPath = signedIn ? pageUrl("profile") : pageUrl("login");
  const displayName = user?.full_name || user?.username || "";
  const header = `
    <a class="skip-link" href="#main-content">Skip to main content</a>
    <header class="site-header">
      <div class="container site-header__inner">
        <a class="logo" href="${pageUrl("home")}" aria-label="Cartly â€” home">cartly</a>
        <nav class="primary-nav" id="primary-nav" aria-label="Primary">
          <div class="nav-shortcuts" aria-label="Store shortcuts">
            <a href="${pageUrl("home")}">Home</a>
            <a href="${pageUrl("cart")}">Cart</a>
            <a href="${pageUrl("wishlist")}">Wishlist</a>
          </div>
          <a href="${pageUrl("products")}"${activeShop ? ' aria-current="page"' : ""}>Shop</a>
          <details class="nav-drop">
            <summary>Categories<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></summary>
            <ul><li><a href="${pageUrl("products")}">All products</a></li></ul>
          </details>
          <div class="nav-account">
            <p class="nav-account__title">Account</p>
            ${signedIn
              ? `<a href="${pageUrl("profile")}">My profile</a><a href="${pageUrl("orders")}">My orders</a><a href="${pageUrl("wishlist")}">Wishlist</a><button class="nav-link-button" type="button" data-action="logout">Sign out</button>`
              : `<button class="nav-link-button" type="button" data-header-auth-open="login">Sign in</button><button class="nav-link-button" type="button" data-header-auth-open="register">Create account</button>`}
          </div>
        </nav>
        <form class="site-search" role="search" action="${pageUrl("products")}" method="get">
          <label class="sr-only" for="site-search-input">Search products</label>
          <input class="input" id="site-search-input" type="search" name="q" placeholder="Search" autocomplete="off" enterkeyhint="search">
          <button class="site-search__btn" type="submit" aria-label="Search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg></button>
        </form>
        <div class="header-actions">
          ${signedIn ? `<a class="action-link action-link--wishlist" href="${pageUrl("wishlist")}">${heartIcon}<span class="action-link__text">Wishlist</span>${badge(wishlistCount)}</a>` : ""}
          <a class="action-link" href="${pageUrl("cart")}">${cartIcon}<span class="action-link__text">Cart</span>${badge(cartCount)}</a>
          ${signedIn ? "" : `<button class="mobile-account-trigger action-link" type="button" data-header-auth-open="login" aria-label="Sign in">${userIcon}<span class="action-link__text">Sign in</span></button>`}
          ${signedIn
            ? `<details class="user-menu"><summary class="action-link" aria-label="Account menu for ${escapeHtml(displayName)}">${userIcon}<span class="action-link__text">${escapeHtml(displayName)}</span></summary><div class="user-menu__panel"><div class="user-menu__who"><strong>${escapeHtml(displayName)}</strong>${escapeHtml(user.email)}</div><a href="${pageUrl("profile")}">My profile</a><a href="${pageUrl("orders")}">My orders</a><a href="${pageUrl("wishlist")}">Wishlist</a><button type="button" data-action="logout">Sign out</button></div></details>`
            : `<details class="user-menu user-menu--guest"><summary class="action-link" aria-label="Sign in or create an account">${userIcon}<span class="action-link__text">Sign in</span></summary>
              <div class="user-menu__panel header-auth" aria-label="Account access">
                <button class="header-auth__close" type="button" data-header-auth-close aria-label="Close account form">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
                </button>
                <section class="header-auth__section" data-header-auth-view="login" aria-labelledby="header-login-title">
                  <h2 id="header-login-title">Sign in</h2>
                  <form id="header-login-form" class="header-auth__form">
                    <div class="field"><label class="field__label" for="header-login-email">Email address <span class="req" aria-hidden="true">*</span></label><input class="input" id="header-login-email" name="email" type="email" autocomplete="email" required></div>
                    <div class="field"><label class="field__label" for="header-login-password">Password <span class="req" aria-hidden="true">*</span></label><div class="pw-wrap"><input class="input" id="header-login-password" name="password" type="password" autocomplete="current-password" required><button class="pw-toggle" type="button" aria-controls="header-login-password" aria-pressed="false" aria-label="Show password" data-label="password">Show</button></div></div>
                    <button class="btn btn--primary btn--block" type="submit">Sign in</button>
                  </form>
                  <p class="header-auth__switch">New to Cartly? <button type="button" data-header-auth-switch="register">Create an account</button></p>
                </section>
                <section class="header-auth__section" data-header-auth-view="register" aria-labelledby="header-register-title" hidden>
                  <h2 id="header-register-title">Create your account</h2>
                  <form id="header-register-form" class="header-auth__form">
                    <div class="field"><label class="field__label" for="header-register-name">Full name <span class="req" aria-hidden="true">*</span></label><input class="input" id="header-register-name" name="full_name" autocomplete="name" maxlength="150" required></div>
                    <div class="field"><label class="field__label" for="header-register-email">Email address <span class="req" aria-hidden="true">*</span></label><input class="input" id="header-register-email" name="email" type="email" autocomplete="email" required></div>
                    <div class="field"><label class="field__label" for="header-register-password">Password <span class="req" aria-hidden="true">*</span></label><div class="pw-wrap"><input class="input" id="header-register-password" name="password1" type="password" autocomplete="new-password" minlength="8" required><button class="pw-toggle" type="button" aria-controls="header-register-password" aria-pressed="false" aria-label="Show password" data-label="password">Show</button></div><p class="field__hint">Use at least 8 characters.</p></div>
                    <div class="field"><label class="field__label" for="header-register-confirm">Confirm password <span class="req" aria-hidden="true">*</span></label><div class="pw-wrap"><input class="input" id="header-register-confirm" name="password2" type="password" autocomplete="new-password" minlength="8" required><button class="pw-toggle" type="button" aria-controls="header-register-confirm" aria-pressed="false" aria-label="Show confirmation password" data-label="confirmation password">Show</button></div></div>
                    <button class="btn btn--primary btn--block" type="submit">Create account</button>
                  </form>
                  <p class="header-auth__switch">Already have an account? <button type="button" data-header-auth-switch="login">Sign in</button></p>
                </section>
              </div></details>`}
        </div>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Menu">
          <span class="icon-open"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></span>
          <span class="icon-close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></span>
        </button>
      </div>
    </header>
    <div class="container messages" id="messages" aria-live="polite"></div>`;

  const footer = `
    <footer class="site-footer"><div class="container">
      <div class="footer-grid">
        <div class="footer-brand"><a class="logo" href="${pageUrl("home")}" aria-label="Cartly â€” home">cartly</a><p>Thoughtful finds. Everyday value.</p></div>
        <nav class="footer-col" aria-label="Explore"><h2>Explore</h2><ul><li><a href="${pageUrl("products")}">All products</a></li><li><a href="${pageUrl("cart")}">Your cart</a></li></ul></nav>
        <nav class="footer-col" aria-label="Account"><h2>Your account</h2><ul>${signedIn ? `<li><a href="${pageUrl("profile")}">My profile</a></li><li><a href="${pageUrl("orders")}">My orders</a></li><li><a href="${pageUrl("wishlist")}">Wishlist</a></li>` : `<li><a href="${pageUrl("login")}">Sign in</a></li><li><a href="${pageUrl("register")}">Create account</a></li>`}</ul></nav>
        <section class="footer-developer" aria-labelledby="footer-developer-heading">
          <h2 id="footer-developer-heading">Developer</h2>
          <div class="footer-developer__profile">
            <img src="${assetUrl("developer.jpg")}" alt="MD. Shoaib Sikder" loading="lazy">
            <div>
              <p class="footer-developer__name">MD. Shoaib Sikder</p>
              <div class="footer-socials" aria-label="Developer links">
                ${developerSocialLinks.map(({ label, href, icon }) => `<a href="${href}" target="_blank" rel="noreferrer" aria-label="MD. Shoaib Sikder on ${label}" title="${label}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icon}</svg></a>`).join("")}
              </div>
            </div>
          </div>
        </section>
      </div>
      <div class="footer-legal"><p>© ${new Date().getFullYear()} Cartly. All rights reserved.</p><p>Made with <span class="footer-heart" aria-hidden="true">&hearts;</span> by MD. Shoaib Sikder</p></div>
    </div></footer>
    <nav class="bottom-nav" aria-label="Quick navigation">
      <a href="${pageUrl("home")}">${homeIcon}Home</a><a href="${pageUrl("products")}">${shopIcon}Shop</a>
      <a href="${pageUrl("wishlist")}">${heartIcon}Wishlist${signedIn ? badge(wishlistCount) : ""}</a><a href="${pageUrl("cart")}">${cartIcon}Cart${badge(cartCount)}</a>
      <a href="${accountPath}">${userIcon}${signedIn ? "Account" : "Sign in"}</a>
    </nav>
    <div class="sr-only" id="live-region" role="status" aria-live="polite" aria-atomic="true"></div>`;

  document.body.classList.add("has-bottom-nav");
  document.body.insertAdjacentHTML("afterbegin", header);
  document.body.insertAdjacentHTML("beforeend", footer);
  const search = document.querySelector("#site-search-input");
  search.value = new URLSearchParams(window.location.search).get("q") || "";
  bindNavigation();
}

export function populateCategories(categories) {
  const list = document.querySelector(".nav-drop ul");
  if (!list) return;
  list.innerHTML = categories.length
    ? categories.map((item) => {
      const category = typeof item === "string" ? item : item.category;
      return `<li><a href="${pageUrl("products", { category })}">${escapeHtml(category)}</a></li>`;
    }).join("")
    : `<li><a href="${pageUrl("products")}">All products</a></li>`;

  const footerList = document.querySelector('.footer-col[aria-label="Shop"] ul');
  if (footerList && categories.length) {
    footerList.insertAdjacentHTML("beforeend", categories.map((item) => {
      const category = typeof item === "string" ? item : item.category;
      return `<li><a href="${pageUrl("products", { category })}">${escapeHtml(category)}</a></li>`;
    }).join(""));
  }
}

function bindNavigation() {
  const button = document.querySelector(".menu-toggle");
  const nav = document.querySelector("#primary-nav");
  const guestMenu = document.querySelector(".user-menu--guest");
  if (button && nav) {
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      nav.classList.toggle("is-open", !expanded);
    });
    document.addEventListener("click", (event) => {
      if (!nav.contains(event.target) && !button.contains(event.target) && !guestMenu?.contains(event.target)) {
        button.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    });
  }

  if (guestMenu) {
    const headerActions = document.querySelector(".header-actions");
    const phoneLayout = window.matchMedia("(max-width: 639.98px)");
    const placeGuestMenu = () => {
      const destination = phoneLayout.matches ? document.body : headerActions;
      if (destination && guestMenu.parentElement !== destination) {
        destination.append(guestMenu);
      }
      const authPanel = guestMenu.querySelector(".header-auth");
      if (phoneLayout.matches) {
        authPanel?.setAttribute("role", "dialog");
        authPanel?.setAttribute("aria-modal", "true");
      } else {
        authPanel?.removeAttribute("role");
        authPanel?.removeAttribute("aria-modal");
      }
    };
    placeGuestMenu();
    phoneLayout.addEventListener("change", placeGuestMenu);

    document.addEventListener("click", (event) => {
      const authTrigger = event.target instanceof Element
        && event.target.closest("[data-header-auth-open]");
      if (phoneLayout.matches && guestMenu.open) return;
      if (!guestMenu.contains(event.target) && !authTrigger) guestMenu.open = false;
    });
  }

  document.querySelectorAll("[data-action='logout']").forEach((logoutButton) => {
    logoutButton.addEventListener("click", async (event) => {
      event.preventDefault();
      logoutButton.disabled = true;
      try {
        await signOut();
        window.location.assign(pageUrl("home"));
      } catch (error) {
        logoutButton.disabled = false;
        showMessage(friendlyErrorMessage(error), "error");
      }
    });
  });
}

export function showMessage(message, type = "info") {
  const region = document.querySelector("#messages");
  if (!region) return;
  const alert = document.createElement("div");
  alert.className = `alert alert--${type}`;
  alert.setAttribute("role", type === "error" ? "alert" : "status");
  alert.innerHTML = `<span class="alert__icon" aria-hidden="true"></span><div class="alert__body"></div><button class="alert__close" type="button" aria-label="Dismiss message">Ã—</button>`;
  alert.querySelector(".alert__body").textContent = message;
  alert.querySelector(".alert__close").addEventListener("click", () => alert.remove());
  region.append(alert);
}

export function announce(message) {
  const region = document.querySelector("#live-region");
  if (region) region.textContent = message;
}
