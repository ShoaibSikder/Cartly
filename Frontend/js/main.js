import { getCurrentUser } from "./api/account-api.js?v=cartly-auth-20261021";
import { getCart } from "./api/cart-api.js?v=cartly-auth-20261021";
import { getWishlist } from "./api/wishlist-api.js?v=cartly-auth-20261021";
import { friendlyErrorMessage } from "./api/api-client.js?v=cartly-auth-csrf-20261021";
import { renderShell } from "./components/shell.js?v=cartly-product-images-20261021-1";
import { pageTitle, pageUrl } from "./config.js?v=cartly-account-sidebar-20261021";

async function start() {
  const main = document.querySelector("#main-content");
  const pageName = document.body.dataset.page || "home";
  let user;
  let cart;
  let wishlist = [];

  try {
    const [account, cartData] = await Promise.all([getCurrentUser(), getCart()]);
    user = account.user;
    cart = cartData;
    if (user) wishlist = await getWishlist();
  } catch (error) {
    console.error("Cartly failed to load account and cart data.", error);
    main.innerHTML = `<div class="container page"><section class="error-page" role="alert"><h1>We’re having trouble loading the store</h1><p class="text-muted"></p><div class="error-page__actions"><button class="btn btn--primary" id="retry-store" type="button">Try again</button><a class="btn btn--secondary" href="${pageUrl("home")}">Return home</a></div></section></div>`;
    main.querySelector(".error-page p").textContent = friendlyErrorMessage(
      error,
      "Some store information didn’t load. Please try again in a moment.",
    );
    main.querySelector("#retry-store").addEventListener("click", () => window.location.reload());
    return;
  }

  renderShell(user, cart.count, pageName, wishlist.length);
  try {
    const accountPage = await import("./pages/account.js?v=cartly-product-images-20261021-1");
    accountPage.bindHeaderAuthForms();
    const pages = {
      home: async () => (await import("./pages/home.js?v=cartly-product-images-20261021-1")).renderHome(user),
      products: async () => (await import("./pages/catalog.js?v=cartly-product-images-20261021-1")).renderProducts(user),
      product: async () => (await import("./pages/catalog.js?v=cartly-product-images-20261021-1")).renderProduct(user),
      profile: async () => (await import("./pages/account.js?v=cartly-product-images-20261021-1")).renderProfile(user),
      cart: async () => (await import("./pages/commerce.js?v=cartly-product-images-20261021-1")).renderCart(),
      checkout: async () => (await import("./pages/commerce.js?v=cartly-product-images-20261021-1")).renderCheckout(user),
      orders: async () => (await import("./pages/commerce.js?v=cartly-product-images-20261021-1")).renderOrders(user),
      order: async () => (await import("./pages/commerce.js?v=cartly-product-images-20261021-1")).renderOrder(user),
      "order-success": async () => (await import("./pages/commerce.js?v=cartly-product-images-20261021-1")).renderOrder(user, true),
      wishlist: async () => (await import("./pages/community.js?v=cartly-product-images-20261021-1")).renderWishlist(user),
      reviews: async () => (await import("./pages/community.js?v=cartly-product-images-20261021-1")).renderReviews(user),
    };
    const render = pages[pageName];
    if (!render) {
      document.title = pageTitle("Page not found");
      main.innerHTML = `<div class="container page"><div class="error-page"><p class="error-page__code" aria-hidden="true">404</p><h1>Page not found</h1><p>This page is no longer available.</p><div class="error-page__actions"><a class="btn btn--primary" href="${pageUrl("home")}">Go to home</a><a class="btn btn--secondary" href="${pageUrl("products")}">Browse products</a></div></div></div>`;
      return;
    }
    await render();
  } catch (error) {
    console.error(`Cartly failed to render the ${pageName} page.`, error);
    main.innerHTML = `<div class="container page"><div class="error-page"><h1>This page didn’t load</h1><p class="text-muted"></p><div class="error-page__actions"><a class="btn btn--primary" href="${pageUrl("home")}">Go to home</a><a class="btn btn--secondary" href="${window.location.pathname}${window.location.search}">Try again</a></div></div></div>`;
    main.querySelector(".error-page p.text-muted").textContent = friendlyErrorMessage(error);
  }
}

start();
