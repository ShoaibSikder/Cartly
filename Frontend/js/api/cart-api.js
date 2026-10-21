import { api } from "./api-client.js?v=cartly-auth-csrf-20261021";

export function getCart() {
  return api("/cart/");
}

export function addCartItem(productId, quantity) {
  return api(`/cart/items/${productId}/`, {
    method: "POST",
    body: { quantity },
  });
}

export function updateCartItem(productId, quantity) {
  return api(`/cart/items/${productId}/`, {
    method: "PUT",
    body: { quantity },
  });
}

export function removeCartItem(productId) {
  return api(`/cart/items/${productId}/`, { method: "DELETE" });
}
