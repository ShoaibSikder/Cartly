import { getProduct, getProductReviews, submitProductReview } from "../api/store-api.js?v=cartly-auth-20261021";
import { friendlyErrorMessage } from "../api/api-client.js?v=cartly-auth-csrf-20261021";
import { getWishlist } from "../api/wishlist-api.js?v=cartly-auth-20261021";
import { pageTitle, pageUrl } from "../config.js?v=cartly-account-sidebar-20261021";
import { bindWishlistButtons, escapeHtml, renderProductCard } from "../components/products.js?v=cartly-product-images-20261021-1";
import { showMessage } from "../components/shell.js?v=cartly-product-images-20261021-1";

export async function renderWishlist(user) {
  if (!user) {
    window.location.assign(pageUrl("login", { next: pageUrl("wishlist") }));
    return;
  }
  const products = await getWishlist();
  document.title = pageTitle("Your wishlist");
  document.querySelector("#wishlist-description").textContent =
    `${products.length} saved item${products.length === 1 ? "" : "s"}. Only you can see this list.`;
  const grid = document.querySelector("#wishlist-grid");
  const empty = document.querySelector("#wishlist-empty");
  grid.hidden = products.length === 0;
  empty.hidden = products.length !== 0;
  grid.innerHTML = products.map((product) => renderProductCard(product, user, true)).join("");
  bindWishlistButtons(user, () => window.location.reload());
}

export async function renderReviews(user) {
  const params = new URLSearchParams(window.location.search);
  const slug = params.get("slug");
  if (!slug) {
    window.location.replace(pageUrl("products"));
    return;
  }
  const [product, data] = await Promise.all([
    getProduct(slug),
    getProductReviews(slug),
  ]);
  document.title = pageTitle(`${product.name} reviews`);
  const myReview = data.my_review;
  const productLink = document.querySelector("#reviews-product-link");
  productLink.textContent = product.name;
  productLink.href = pageUrl("product", { slug });
  document.querySelector("#reviews-product-description").textContent =
    `${product.name} · Reviews appear publicly after staff approval.`;
  document.querySelector("#reviews-average").textContent = data.average_rating !== null
    ? Number(data.average_rating).toFixed(1)
    : "–";
  document.querySelector("#reviews-stars").style.setProperty("--rating", data.average_rating || 0);
  document.querySelector("#reviews-stars").setAttribute(
    "aria-label",
    data.average_rating !== null ? `${Number(data.average_rating).toFixed(1)} out of 5 stars` : "No ratings yet",
  );
  document.querySelector("#reviews-count").textContent = data.review_count
    ? `Based on ${data.review_count} displayed approved review${data.review_count === 1 ? "" : "s"}`
    : "No approved reviews yet. Be the first to share your experience.";
  document.querySelector("#review-authorized").hidden = !user;
  document.querySelector("#review-unauthorized").hidden = Boolean(user);
  document.querySelector("#review-signin").href = pageUrl("login", {
    next: `${pageUrl("reviews", { slug })}#review-form`,
  });
  if (user) {
    document.querySelector("#review-form-title").textContent =
      myReview ? "Update your review" : "Write a review";
    document.querySelector("#pending-review-message").hidden =
      !myReview || myReview.is_approved;
    document.querySelector("#review-title").value = myReview?.title || "";
    document.querySelector("#review-body").value = myReview?.body || "";
    document.querySelector(`#rating-${Number(myReview?.rating || 5)}`).checked = true;
  }
  const reviewList = document.querySelector("#review-list");
  const pendingReview = myReview && !myReview.is_approved
    ? `<li class="card review review--pending">${reviewContent(myReview, true)}<p class="text-small text-muted review-pending__note">Only you can see this until staff approve it.</p></li>`
    : "";
  reviewList.innerHTML = `${pendingReview}${data.reviews.map((review) => `<li class="card review">${reviewContent(review, false)}</li>`).join("")}`;
  document.querySelector("#reviews-empty").hidden =
    data.reviews.length > 0 || Boolean(pendingReview);
  document.querySelector("#review-submit")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button[type="submit"]');
    if (!event.currentTarget.querySelector('input[name="rating"]:checked')) {
      showMessage("Choose a rating before submitting your review.", "error");
      event.currentTarget.querySelector('input[name="rating"]')?.focus();
      return;
    }
    button.disabled = true;
    try {
      await submitProductReview(
        slug,
        Object.fromEntries(new FormData(event.currentTarget)),
      );
      showMessage("Your review was submitted for approval.", "success");
      window.setTimeout(() => window.location.reload(), 600);
    } catch (error) {
      showMessage(friendlyErrorMessage(error), "error");
      button.disabled = false;
    }
  });
}

function reviewContent(review, pending) {
  const title = review.title ? `<h2 class="review__title">${escapeHtml(review.title)}</h2>` : "";
  const badge = pending ? '<span class="badge badge--warning">Pending moderation</span>' : "";
  const author = review.user_name || "";
  return `<div class="review__head"><span class="stars" style="--rating:${review.rating}" role="img" aria-label="${review.rating} out of 5 stars">★★★★★</span>${title}${badge}</div>
    <p class="review__meta"><span>${escapeHtml(author)}</span><span aria-hidden="true">·</span><time datetime="${escapeHtml(review.created_at)}">${new Date(review.created_at).toLocaleDateString()}</time></p>
    <p class="review__text">${escapeHtml(review.body)}</p>`;
}
