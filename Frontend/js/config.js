const configuredApiOrigin = new URLSearchParams(window.location.search).get("api");
const savedApiOrigin = window.localStorage.getItem("cartly-api-origin");
const defaultApiOrigin = new URL(window.location.origin);
defaultApiOrigin.port = "8000";

const requestedApiOrigin = (
  window.CARTLY_API_ORIGIN || configuredApiOrigin || savedApiOrigin || defaultApiOrigin.origin
).trim().replace(/\/+$/, "");
const resolvedApiOrigin = new URL(requestedApiOrigin, window.location.origin);
const localHosts = new Set(["localhost", "127.0.0.1"]);
if (localHosts.has(window.location.hostname) && localHosts.has(resolvedApiOrigin.hostname)) {
  resolvedApiOrigin.hostname = window.location.hostname;
}
export const API_ORIGIN = resolvedApiOrigin.origin;
export const API_BASE = `${API_ORIGIN}/api/v1`;
const pageDirectory = window.location.pathname
  .replace(/\/pages\/[^/]+$/, "")
  .replace(/\/[^/]+\.html$/, "");
const frontendDirectory = pageDirectory === "/" ? "" : pageDirectory.replace(/\/$/, "");
export const FRONTEND_BASE = window.CARTLY_FRONTEND_BASE
  ?? frontendDirectory;

if (configuredApiOrigin) {
  window.localStorage.setItem("cartly-api-origin", API_ORIGIN);
}

export const assetUrl = (name) => `${FRONTEND_BASE}/assets/${name}`;

export const pages = {
  home: `${FRONTEND_BASE}/index.html`,
  products: `${FRONTEND_BASE}/pages/products.html`,
  product: `${FRONTEND_BASE}/pages/product_detail.html`,
  login: `${FRONTEND_BASE}/index.html?account=login`,
  register: `${FRONTEND_BASE}/index.html?account=register`,
  profile: `${FRONTEND_BASE}/pages/profile.html`,
  cart: `${FRONTEND_BASE}/pages/cart.html`,
  checkout: `${FRONTEND_BASE}/pages/checkout.html`,
  orders: `${FRONTEND_BASE}/pages/orders.html`,
  order: `${FRONTEND_BASE}/pages/order.html`,
  orderSuccess: `${FRONTEND_BASE}/pages/order_success.html`,
  wishlist: `${FRONTEND_BASE}/pages/wishlist.html`,
  reviews: `${FRONTEND_BASE}/pages/reviews.html`,
};

export function pageUrl(name, params = {}) {
  const url = new URL(pages[name], window.location.origin);
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") {
      url.searchParams.set(key, value);
    }
  }
  return `${url.pathname}${url.search}`;
}

export function pageTitle(label) {
  return `${label} | Cartly`;
}
