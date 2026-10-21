import { api } from "./api-client.js?v=cartly-auth-csrf-20261021";

export function getWishlist() {
  return api("/wishlist/");
}

export function setWishlistState(productId, saved) {
  return api(`/wishlist/items/${productId}/`, {
    method: saved ? "POST" : "DELETE",
  });
}
