import { api } from "./api-client.js?v=cartly-auth-csrf-20261021";

export function getHomeData() {
  return api("/home/");
}

export function getProducts(params) {
  const query = params.toString();
  return api(`/products/${query ? `?${query}` : ""}`);
}

export function getProduct(slug) {
  return api(`/products/${encodeURIComponent(slug)}/`);
}

export function getProductReviews(slug) {
  return api(`/products/${encodeURIComponent(slug)}/reviews/`);
}

export function submitProductReview(slug, review) {
  return api(`/products/${encodeURIComponent(slug)}/reviews/`, {
    method: "POST",
    body: review,
  });
}
