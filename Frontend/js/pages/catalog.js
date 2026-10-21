import { addCartItem } from "../api/cart-api.js?v=cartly-auth-20261021";
import { friendlyErrorMessage } from "../api/api-client.js?v=cartly-auth-csrf-20261021";
import { getProduct, getProductReviews, getProducts } from "../api/store-api.js?v=cartly-auth-20261021";
import { assetUrl, pageTitle, pageUrl } from "../config.js?v=cartly-account-sidebar-20261021";
import {
  bindWishlistButtons,
  escapeHtml,
  formatPrice,
  productImage,
  renderProductCard,
} from "../components/products.js?v=cartly-product-images-20261021-1";
import { populateCategories, showMessage } from "../components/shell.js?v=cartly-product-images-20261021-1";

function currentParams() {
  return new URLSearchParams(window.location.search);
}

function formParams(form) {
  const params = new URLSearchParams();
  new FormData(form).forEach((value, key) => {
    if (String(value).trim()) params.append(key, value);
  });
  return params;
}

export async function renderProducts(user) {
  const params = currentParams();
  const data = await getProducts(params);
  populateCategories(data.categories);
  const query = params.get("q") || "";
  const selectedCategories = params.getAll("category");
  const sort = params.get("sort") || "featured";
  document.title = pageTitle(query ? `Search: ${query}` : "Products");
  document.querySelector("#catalogue-description").textContent = query
    ? `Showing products that match “${query}”.`
    : "Find the right product without the clutter.";
  document.querySelector("#catalogue-count").textContent =
    `${data.count} product${data.count === 1 ? "" : "s"}`;
  const filtersForm = document.querySelector("#filters-form");
  filtersForm.querySelectorAll('input[name="category"]').forEach((input) => input.remove());
  filtersForm.action = pageUrl("products");
  document.querySelector("#filter-query").value = query;
  document.querySelector("#filter-sort").value = sort;
  document.querySelector("#min").value = params.get("min") || "";
  document.querySelector("#max").value = params.get("max") || "";
  filtersForm.querySelector('[name="stock"]').checked = params.get("stock") === "1";
  document.querySelector("#category-filters").innerHTML = data.categories.length
    ? data.categories.map((category) => `<label class="check"><input type="checkbox" name="category" value="${escapeHtml(category)}"${selectedCategories.includes(category) ? " checked" : ""}><span>${escapeHtml(category)}</span></label>`).join("")
    : '<p class="text-muted text-small">No categories yet.</p>';
  document.querySelector("#sort").value = sort;
  const hiddenFilters = [["q", query], ...selectedCategories.map((category) => ["category", category]), ["min", params.get("min")], ["max", params.get("max")], ["stock", params.get("stock")]]
    .filter(([, value]) => value)
    .map(([key, value]) => `<input type="hidden" name="${key}" value="${escapeHtml(value)}">`)
    .join("");
  document.querySelector("#sort-hidden-filters").innerHTML = hiddenFilters;
  const productList = document.querySelector("#product-list");
  productList.innerHTML = data.results.length
    ? data.results.map((product) => renderProductCard(product, user)).join("")
    : `<li class="empty-state"><img src="${assetUrl("empty-state.svg")}" alt="" width="128" height="96"><h2>No products found</h2><p>Try another search or clear your filters.</p><a class="btn btn--primary" href="${pageUrl("products")}">Browse all products</a></li>`;
  const pagination = document.querySelector("#product-pagination");
  pagination.hidden = data.total_pages <= 1;
  pagination.querySelector("ul").innerHTML = renderPaginationItems(data, params);

  filtersForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const next = formParams(filtersForm);
    window.location.assign(`${pageUrl("products")}?${next}`);
  });
  const sortForm = document.querySelector("#sort-form");
  sortForm.action = pageUrl("products");
  sortForm.addEventListener("submit", (event) => {
    event.preventDefault();
    window.location.assign(`${pageUrl("products")}?${formParams(event.currentTarget)}`);
  });
  const filtersButton = document.querySelector("#filters-toggle");
  filtersButton.addEventListener("click", () => {
    const expanded = filtersButton.getAttribute("aria-expanded") === "true";
    filtersButton.setAttribute("aria-expanded", String(!expanded));
    document.querySelector("#filters").classList.toggle("is-open", !expanded);
  });
  bindWishlistButtons(user);
}

function renderPaginationItems(data, params) {
  if (data.total_pages <= 1) return "";
  const item = (page, label, disabled = false, current = false) => {
    const next = new URLSearchParams(params);
    next.set("page", String(page));
    return `<li>${disabled ? `<span class="is-disabled">${label}</span>` : current ? `<span aria-current="page">${label}</span>` : `<a href="${pageUrl("products")}?${next}" aria-label="${label === "Previous" || label === "Next" ? `${label} page` : `Page ${page}`}">${label}</a>`}</li>`;
  };
  const pages = [];
  for (let page = 1; page <= data.total_pages; page += 1) {
    pages.push(item(page, String(page), false, page === data.page));
  }
  return `${item(data.page - 1, "Previous", data.page <= 1)}${pages.join("")}${item(data.page + 1, "Next", data.page >= data.total_pages)}`;
}

export async function renderProduct(user) {
  const slug = currentParams().get("slug");
  if (!slug) {
    window.location.replace(pageUrl("products"));
    return;
  }
  const product = await getProduct(slug);
  const reviews = await getProductReviews(slug);
  const reviewList = reviews.reviews.slice(0, 4).map(renderReview).join("");
  document.title = pageTitle(product.name);
  document.querySelector("#product-category-link").href = product.category
    ? pageUrl("products", { category: product.category })
    : pageUrl("products");
  document.querySelector("#product-breadcrumb").textContent = product.name;
  document.querySelector("#product-name").textContent = product.name;
  document.querySelector("#product-image").innerHTML = productImage(product, "");
  document.querySelector("#product-price").textContent = formatPrice(product.price);
  document.querySelector("#product-description").textContent = product.description;
  document.querySelector("#product-details").textContent = product.description;
  const category = document.querySelector("#product-category");
  category.hidden = !product.category;
  category.textContent = product.category ? `Category: ${product.category}` : "";
  if (product.category) {
    category.innerHTML = `Category: <a href="${pageUrl("products", { category: product.category })}">${escapeHtml(product.category)}</a>`;
  }

  const stockLabel = document.createElement("span");
  stockLabel.className = `stock ${product.stock === 0 ? "stock--out" : product.stock <= 5 ? "stock--low" : "stock--in"}`;
  stockLabel.textContent = product.stock === 0
    ? "Out of stock"
    : product.stock <= 5 ? `Only ${product.stock} left` : "In stock";
  document.querySelector("#product-stock").replaceChildren(stockLabel);
  const cartForm = document.querySelector("#add-cart-form");
  cartForm.hidden = product.stock === 0;
  cartForm.dataset.productId = product.id;
  document.querySelector("#out-of-stock").hidden = product.stock !== 0;
  const quantity = document.querySelector("#qty-input");
  quantity.max = product.stock;
  document.querySelector("#qty-note").textContent = `Up to ${product.stock} per order.`;
  const stepUp = cartForm.querySelector('[data-step="1"]');
  stepUp.disabled = product.stock === 1;
  const wishlistButton = document.querySelector("#product-wishlist");
  wishlistButton.hidden = false;
  wishlistButton.dataset.wishlist = product.id;
  wishlistButton.dataset.productName = product.name;
  wishlistButton.setAttribute("aria-label", `${product.in_wishlist ? "Remove" : "Add"} ${product.name} ${product.in_wishlist ? "from" : "to"} wishlist`);
  wishlistButton.setAttribute("aria-pressed", String(product.in_wishlist));
  wishlistButton.textContent = product.in_wishlist ? "Saved to wishlist" : "Save to wishlist";

  document.querySelector("#product-rating").innerHTML = reviews.review_count
    ? `<span class="rating-line"><span class="stars" style="--rating:${Number(reviews.average_rating)}" role="img" aria-label="${Number(reviews.average_rating).toFixed(1)} out of 5 stars">★★★★★</span><span class="rating-line__num">${Number(reviews.average_rating).toFixed(1)}</span><span class="rating-line__count">· ${reviews.review_count} approved review${reviews.review_count === 1 ? "" : "s"}</span></span>`
    : '<span class="rating-line text-muted">No reviews yet</span>';
  document.querySelector("#product-review-count").textContent = reviews.review_count;
  document.querySelector("#review-average").textContent =
    reviews.review_count ? Number(reviews.average_rating).toFixed(1) : "–";
  document.querySelector("#review-stars").style.setProperty("--rating", reviews.average_rating || 0);
  document.querySelector("#review-stars").setAttribute(
    "aria-label",
    reviews.review_count ? `${Number(reviews.average_rating).toFixed(1)} out of 5 stars` : "No ratings yet",
  );
  document.querySelector("#review-count-label").textContent = reviews.review_count
    ? `Based on ${reviews.review_count} approved reviews`
    : "No reviews yet. Be the first to share your experience.";
  document.querySelector("#write-review-link").href = `${pageUrl("reviews", { slug })}#review-form`;
  const reviewContainer = document.querySelector("#product-review-list");
  reviewContainer.innerHTML = reviewList || `<div class="empty-state"><p>No approved reviews yet.</p><a class="btn btn--secondary" href="${pageUrl("reviews", { slug })}#review-form">Be the first to review</a></div>`;
  const related = document.querySelector("#related-products");
  related.innerHTML = product.related_products.map((item) => renderProductCard(item, user)).join("");
  document.querySelector("#related-section").hidden = product.related_products.length === 0;

  cartForm.addEventListener("submit", addToCart);
  document.querySelectorAll(".qty button[data-step]").forEach((button) => button.addEventListener("click", () => {
    const input = document.querySelector("#qty-input");
    const value = Number(input.value);
    input.value = String(Math.max(Number(input.min), Math.min(Number(input.max), value + Number(button.dataset.step))));
    document.querySelector('.qty [data-step="-1"]').disabled = Number(input.value) <= 1;
    document.querySelector('.qty [data-step="1"]').disabled = Number(input.value) >= Number(input.max);
  }));
  bindWishlistButtons(user);
}

async function addToCart(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button[type="submit"]');
  const quantity = event.currentTarget.querySelector('input[name="quantity"]');
  const requested = Number(quantity.value);
  if (!Number.isInteger(requested) || requested < 1 || requested > Number(quantity.max)) {
    showMessage(`Enter a quantity between 1 and ${quantity.max}.`, "error");
    quantity.focus();
    return;
  }
  button.disabled = true;
  try {
    await addCartItem(
      event.currentTarget.dataset.productId,
      requested,
    );
    showMessage("Added to your cart.", "success");
    window.setTimeout(() => window.location.assign(pageUrl("cart")), 500);
  } catch (error) {
    showMessage(friendlyErrorMessage(error), "error");
    button.disabled = false;
  }
}

function renderReview(review) {
  return `<article class="card review"><div class="review__head"><span class="stars" style="--rating:${review.rating}" role="img" aria-label="${review.rating} out of 5 stars">★★★★★</span>${review.title ? `<h3 class="review__title">${escapeHtml(review.title)}</h3>` : ""}</div><p class="review__meta"><span>${escapeHtml(review.user_name)}</span><span aria-hidden="true">·</span><time datetime="${escapeHtml(review.created_at)}">${new Date(review.created_at).toLocaleDateString()}</time></p><p class="review__text">${escapeHtml(review.body)}</p></article>`;
}
