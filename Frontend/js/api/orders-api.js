import { api } from "./api-client.js?v=cartly-auth-csrf-20261021";

export function getOrders() {
  return api("/orders/");
}

export function placeOrder(details) {
  return api("/orders/", { method: "POST", body: details });
}

export function getOrder(orderId) {
  return api(`/orders/${orderId}/`);
}
