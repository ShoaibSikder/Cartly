import { setWishlistState } from "../api/wishlist-api.js?v=cartly-auth-20261021";
import { friendlyErrorMessage } from "../api/api-client.js?v=cartly-auth-csrf-20261021";
import { assetUrl, pageUrl } from "../config.js?v=cartly-account-sidebar-20261021";
import { announce, showMessage } from "./shell.js?v=cartly-product-images-20261021-1";

export function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[character]);
}

export function formatPrice(value) {
  return Number(value || 0).toFixed(2);
}

export function productImage(product, className = "") {
  return product.image
    ? `<img${className ? ` class="${className}"` : ""} src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}" loading="lazy">`
    : `<span class="product-image-placeholder" role="img" aria-label="${escapeHtml(product.name)} image unavailable"></span>`;
}

export function renderProductCard(product, user, wishlistCard = false) {
  const saved = Boolean(product.in_wishlist || wishlistCard);
  const detailUrl = pageUrl("product", { slug: product.slug });
  return `<li class="product-card${product.stock ? "" : " is-unavailable"}">
    <button class="wish-btn" type="button" data-wishlist="${product.id}" data-product-name="${escapeHtml(product.name)}" aria-pressed="${saved}" aria-label="${saved ? "Remove" : "Add"} ${escapeHtml(product.name)} ${saved ? "from" : "to"} wishlist">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.4-9.4C1.2 7.7 3.4 4.5 6.6 4.5c2 0 3.7 1.1 5.4 3.1 1.7-2 3.4-3.1 5.4-3.1 3.2 0 5.4 3.2 4 6.6-1.9 4.8-9.4 9.4-9.4 9.4z"/></svg>
    </button>
    <a class="product-card__media" href="${detailUrl}" tabindex="-1" aria-hidden="true">${productImage(product)}</a>
    <div class="product-card__body">
      <h3 class="product-card__title"><a href="${detailUrl}">${escapeHtml(product.name)}</a></h3>
      <p class="price">${formatPrice(product.price)}</p>
      <div class="product-card__rating">
        ${product.review_count
          ? `<span class="rating-line"><span class="stars" style="--rating:${Number(product.average_rating || 0)}" role="img" aria-label="${Number(product.average_rating).toFixed(1)} out of 5 stars">★★★★★</span><span class="rating-line__count">(${product.review_count})</span></span>`
          : '<span class="text-muted text-small">No reviews yet</span>'}
      </div>
      ${product.stock <= 5 ? `<div><span class="stock ${product.stock ? "stock--low" : "stock--out"}">${product.stock ? `Only ${product.stock} left` : "Out of stock"}</span></div>` : ""}
      <div class="product-card__foot">
        ${wishlistCard
          ? `<div class="wishlist-actions"><p class="wishlist-saved">${heartSvg()}Saved</p><a class="btn btn--secondary btn--block" href="${detailUrl}">View product</a><button class="btn btn--text btn--danger btn--block" type="button" data-wishlist="${product.id}" data-product-name="${escapeHtml(product.name)}" aria-pressed="true">Remove from wishlist</button></div>`
          : `<a class="btn btn--secondary btn--block" href="${detailUrl}">View product</a>`}
      </div>
    </div>
  </li>`;
}

function heartSvg() {
  return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.4-9.4C1.2 7.7 3.4 4.5 6.6 4.5c2 0 3.7 1.1 5.4 3.1 1.7-2 3.4-3.1 5.4-3.1 3.2 0 5.4 3.2 4 6.6-1.9 4.8-9.4 9.4-9.4 9.4z"/></svg>';
}

export function emptyState(title, message, actionLabel = "Browse products") {
  return `<div class="empty-state"><img src="${assetUrl("empty-state.svg")}" alt="" width="128" height="96"><h2>${escapeHtml(title)}</h2><p>${escapeHtml(message)}</p><a class="btn btn--primary" href="${pageUrl("products")}">${actionLabel}</a></div>`;
}

export function bindWishlistButtons(user, afterRemove) {
  document.querySelectorAll("[data-wishlist]").forEach((button) => {
    button.addEventListener("click", async () => {
      if (!user) {
        const next = button.id === "product-wishlist"
          ? `${window.location.pathname}${window.location.search}`
          : `${window.location.pathname}${window.location.search}${window.location.hash}`;
        window.location.assign(pageUrl("login", { next }));
        return;
      }
      const productId = button.dataset.wishlist;
      const remove = button.getAttribute("aria-pressed") === "true" || button.textContent.includes("Remove");
      button.disabled = true;
      try {
        const result = await setWishlistState(productId, !remove);
        if (result.saved === false) {
          if (afterRemove) afterRemove(button);
          else {
            button.setAttribute("aria-pressed", "false");
            button.setAttribute("aria-label", `Add ${button.dataset.productName || "product"} to wishlist`);
            if (button.id === "product-wishlist") button.textContent = "Save to wishlist";
          }
          announce("Removed from your wishlist.");
        } else {
          button.setAttribute("aria-pressed", "true");
          button.setAttribute("aria-label", `Remove ${button.dataset.productName || "product"} from wishlist`);
          if (button.id === "product-wishlist") button.textContent = "Saved to wishlist";
          showMessage("Saved to your wishlist.", "success");
        }
      } catch (error) {
        showMessage(friendlyErrorMessage(error), "error");
      } finally {
        button.disabled = false;
      }
    });
  });
}
