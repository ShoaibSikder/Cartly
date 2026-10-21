import {
  getProfile,
  registerAccount,
  signIn,
  signOut,
  updateProfile,
} from "../api/account-api.js?v=cartly-auth-20261021";
import { getOrders } from "../api/orders-api.js?v=cartly-auth-20261021";
import { getCart } from "../api/cart-api.js?v=cartly-auth-20261021";
import { getWishlist } from "../api/wishlist-api.js?v=cartly-auth-20261021";
import { friendlyErrorMessage } from "../api/api-client.js?v=cartly-auth-csrf-20261021";
import { pageTitle, pageUrl } from "../config.js?v=cartly-account-sidebar-20261021";
import { showMessage } from "../components/shell.js?v=cartly-product-images-20261021-1";

function nextPage() {
  const next = new URLSearchParams(window.location.search).get("next");
  if (!next) return pageUrl("home");
  try {
    const target = new URL(next, window.location.origin);
    return target.origin === window.location.origin ? `${target.pathname}${target.search}${target.hash}` : pageUrl("home");
  } catch {
    return pageUrl("home");
  }
}

function authErrorMessage(error) {
  if (error.status && error.status !== 400) return friendlyErrorMessage(error);
  if (!error.data || typeof error.data !== "object") return friendlyErrorMessage(error);
  return Object.values(error.data).flatMap((errors) =>
    Array.isArray(errors) ? errors.map((item) => typeof item === "string" ? item : item.message) : [String(errors)]
  ).filter(Boolean).join(" ");
}

export function bindHeaderAuthForms() {
  const loginForm = document.querySelector("#header-login-form");
  const registerForm = document.querySelector("#header-register-form");
  const guestMenu = document.querySelector(".user-menu--guest");
  if (!loginForm || !registerForm || !guestMenu) return;

  let lastAuthTrigger = null;
  const phoneLayout = window.matchMedia("(max-width: 639.98px)");
  const setAuthOpen = (isOpen) => {
    if (isOpen && phoneLayout.matches) {
      const menuButton = document.querySelector(".menu-toggle");
      const primaryNav = document.querySelector("#primary-nav");
      menuButton?.setAttribute("aria-expanded", "false");
      primaryNav?.classList.remove("is-open");
    }
    guestMenu.open = isOpen;
    document.body.classList.toggle("auth-overlay-open", isOpen && phoneLayout.matches);
  };
  bindPasswordToggles(document.querySelector(".header-auth"));
  const closeAuth = () => {
    setAuthOpen(false);
    lastAuthTrigger?.focus();
  };
  const showAuthView = (viewName, focus = false) => {
    guestMenu.querySelectorAll("[data-header-auth-view]").forEach((view) => {
      view.hidden = view.dataset.headerAuthView !== viewName;
    });
    if (focus) {
      const firstField = viewName === "register"
        ? "#header-register-name"
        : "#header-login-email";
      guestMenu.querySelector(firstField)?.focus();
    }
  };

  const requestedView = new URLSearchParams(window.location.search).get("account");
  if (requestedView === "login" || requestedView === "register") {
    if (phoneLayout.matches) lastAuthTrigger = document.querySelector(".menu-toggle");
    setAuthOpen(true);
    showAuthView(requestedView, true);
    const url = new URL(window.location.href);
    url.searchParams.delete("account");
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submit = event.currentTarget.querySelector('button[type="submit"]');
    submit.disabled = true;
    try {
      await signIn(Object.fromEntries(new FormData(event.currentTarget)));
      finishHeaderAuth();
    } catch (error) {
      showMessage(authErrorMessage(error), "error");
      submit.disabled = false;
    }
  });

  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submit = event.currentTarget.querySelector('button[type="submit"]');
    submit.disabled = true;
    try {
      await registerAccount(Object.fromEntries(new FormData(event.currentTarget)));
      finishHeaderAuth();
    } catch (error) {
      showMessage(authErrorMessage(error), "error");
      submit.disabled = false;
    }
  });

  document.querySelectorAll("[data-header-auth-switch]").forEach((switchButton) => {
    switchButton.addEventListener("click", () => {
      showAuthView(switchButton.dataset.headerAuthSwitch, true);
    });
  });

  document.querySelectorAll("[data-header-auth-open]").forEach((openButton) => {
    openButton.addEventListener("click", () => {
      lastAuthTrigger = phoneLayout.matches
        ? (openButton.classList.contains("mobile-account-trigger")
          ? openButton
          : document.querySelector(".menu-toggle"))
        : openButton;
      setAuthOpen(true);
      showAuthView(openButton.dataset.headerAuthOpen, true);
    });
  });

  phoneLayout.addEventListener("change", () => {
    document.body.classList.toggle("auth-overlay-open", guestMenu.open && phoneLayout.matches);
  });
  document.querySelector("[data-header-auth-close]")?.addEventListener("click", closeAuth);
  guestMenu.addEventListener("click", (event) => {
    if (event.target === guestMenu) closeAuth();
  });
  guestMenu.addEventListener("keydown", (event) => {
    if (!guestMenu.open) return;
    if (event.key === "Escape") {
      closeAuth();
      return;
    }
    if (event.key !== "Tab" || !window.matchMedia("(max-width: 639.98px)").matches) return;

    const focusable = [...guestMenu.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])',
    )].filter((element) => element.getClientRects().length);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  });
}

function finishHeaderAuth() {
  const next = new URLSearchParams(window.location.search).get("next");
  if (next) {
    window.location.assign(nextPage());
    return;
  }

  const url = new URL(window.location.href);
  url.searchParams.delete("account");
  window.location.assign(`${url.pathname}${url.search}${url.hash}`);
}

function bindPasswordToggles(root = document) {
  root.querySelectorAll(".pw-toggle").forEach((button) => {
    if (button.dataset.passwordToggleBound) return;
    button.dataset.passwordToggleBound = "true";
    button.addEventListener("click", () => {
      const input = document.getElementById(button.getAttribute("aria-controls"));
      if (!input) return;
      const reveal = input.type === "password";
      input.type = reveal ? "text" : "password";
      button.textContent = reveal ? "Hide" : "Show";
      button.setAttribute("aria-pressed", String(reveal));
      button.setAttribute("aria-label", `${reveal ? "Hide" : "Show"} ${button.dataset.label || "password"}`);
    });
  });
}

export async function renderProfile(user) {
  const [profile, orders, wishlist, cart] = await Promise.all([
    getProfile(),
    getOrders(),
    getWishlist(),
    getCart(),
  ]);
  const initials = (profile.first_name || profile.username || "?").slice(0, 1).toUpperCase();
  document.title = pageTitle("My profile");
  document.querySelector("#profile-avatar").textContent = initials;
  document.querySelector("#first_name").value = profile.first_name;
  document.querySelector("#last_name").value = profile.last_name;
  document.querySelector("#email").value = profile.email;
  document.querySelector("#profile-order-count").textContent = orders.length;
  document.querySelector("#profile-wishlist-count").textContent = wishlist.length;
  document.querySelector("#profile-cart-count").textContent = cart.count;
  document.querySelector("#profile-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const submit = event.currentTarget.querySelector('button[type="submit"]');
    submit.disabled = true;
    try {
      const updatedProfile = await updateProfile(Object.fromEntries(new FormData(event.currentTarget)));
      const accountName = document.querySelector(".user-menu__who strong");
      if (accountName) accountName.textContent = updatedProfile.full_name || updatedProfile.username;
      const accountEmail = document.querySelector(".user-menu__who");
      if (accountEmail) accountEmail.lastChild.textContent = updatedProfile.email;
      showMessage("Your profile has been updated.", "success");
    } catch (error) {
      showMessage(authErrorMessage(error), "error");
    } finally {
      submit.disabled = false;
    }
  });
  document.querySelector(".profile-logout").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await signOut();
      window.location.assign(pageUrl("home"));
    } catch (error) {
      showMessage(friendlyErrorMessage(error), "error");
    }
  });
}
