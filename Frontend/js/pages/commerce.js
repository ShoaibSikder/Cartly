import {
  getCart,
  removeCartItem,
  updateCartItem as saveCartItem,
} from "../api/cart-api.js?v=cartly-auth-20261021";
import { getOrder, getOrders, placeOrder } from "../api/orders-api.js?v=cartly-auth-20261021";
import { friendlyErrorMessage } from "../api/api-client.js?v=cartly-auth-csrf-20261021";
import { pageTitle, pageUrl } from "../config.js?v=cartly-account-sidebar-20261021";
import { escapeHtml, formatPrice, productImage } from "../components/products.js?v=cartly-product-images-20261021-1";
import { showMessage } from "../components/shell.js?v=cartly-product-images-20261021-1";

const params = () => new URLSearchParams(window.location.search);

function itemImage(item) {
  const image = item.product?.image || item.image;
  return image
    ? `<img src="${escapeHtml(image)}" alt="" loading="lazy">`
    : '<span class="product-image-placeholder" aria-hidden="true"></span>';
}

function summaryItem(item) {
  const productName = item.product_name || item.product?.name || "Product";
  const price = item.price_at_purchase || item.unit_price;
  const total = item.line_total || item.total_price;
  return `<li class="summary-item"><span class="summary-item__media" aria-hidden="true">${itemImage(item)}</span><div><p class="summary-item__name">${escapeHtml(productName)}</p><p class="summary-item__qty">Qty ${item.quantity} × ${formatPrice(price)}</p></div><span class="summary-item__price">${formatPrice(total)}</span></li>`;
}

function signInToContinue(target) {
  window.location.assign(pageUrl("login", { next: target }));
}

export async function renderCart() {
  const cart = await getCart();
  document.title = pageTitle("Your cart");
  const items = cart.items;
  const unavailableProducts = items.filter((item) => item.product.stock <= 0);
  const unavailableNotice = document.querySelector("#cart-unavailable .alert__body");
  if (unavailableNotice && unavailableProducts.length) {
    unavailableNotice.textContent = `Remove unavailable items (${unavailableProducts.map((item) => item.product.name).join(", ")}) to continue.`;
  }
  document.querySelector("#cart-layout").hidden = items.length === 0;
  document.querySelector("#cart-empty").hidden = items.length !== 0;
  document.querySelector("#cart-description").textContent =
    items.length ? "Review items before you check out." : "Nothing here yet.";
  document.querySelector("#cart-items").innerHTML = items.map((item) => `<li class="cart-item">
        <a class="cart-item__media" href="${pageUrl("product", { slug: item.product.slug })}" tabindex="-1" aria-hidden="true">${productImage(item.product)}</a>
        <div class="cart-item__info"><h2 class="cart-item__name"><a href="${pageUrl("product", { slug: item.product.slug })}">${escapeHtml(item.product.name)}</a></h2><p class="price">${formatPrice(item.unit_price)}</p>
          ${item.product.stock <= 0 ? '<p class="stock stock--out">Out of stock</p>' : item.quantity > item.product.stock ? `<p class="stock stock--low">Only ${item.product.stock} left</p>` : ""}
        </div>
        <div class="cart-item__controls">
          <form class="qty cart-quantity" data-product="${item.product.id}" role="group" aria-label="Quantity for ${escapeHtml(item.product.name)}">
            <button type="button" data-step="-1" aria-label="Decrease quantity of ${escapeHtml(item.product.name)}"${item.quantity <= 1 ? " disabled" : ""}>−</button>
            <input type="number" name="quantity" inputmode="numeric" min="1" max="${Math.max(item.product.stock, item.quantity)}" value="${item.quantity}" aria-label="Quantity of ${escapeHtml(item.product.name)}">
            <button type="button" data-step="1" aria-label="Increase quantity of ${escapeHtml(item.product.name)}"${item.quantity >= item.product.stock ? " disabled" : ""}>+</button>
            <button class="btn btn--secondary btn--sm" type="submit">Update</button>
          </form>
          <button type="button" class="btn btn--text btn--danger remove-item" data-product="${item.product.id}">Remove</button>
        </div>
        <p class="cart-item__total" aria-label="Line total">${formatPrice(item.total_price)}</p>
      </li>`).join("");
  document.querySelector("#cart-subtotal-label").textContent =
    `Subtotal (${cart.count} item${cart.count === 1 ? "" : "s"})`;
  document.querySelector("#cart-subtotal").textContent = formatPrice(cart.total);
  document.querySelector("#cart-total").textContent = formatPrice(cart.total);
  document.querySelector("#cart-unavailable").hidden = !cart.unavailable;
  const checkoutLink = document.querySelector("#checkout-link");
  checkoutLink.href = pageUrl("checkout");
  checkoutLink.hidden = cart.unavailable;
  document.querySelector("#checkout-disabled").hidden = !cart.unavailable;

  document.querySelectorAll(".cart-quantity").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const input = form.querySelector('input[name="quantity"]');
      const requested = Number(input.value);
      const available = Number(input.max);
      if (!Number.isInteger(requested) || requested < 1 || requested > available) {
        showMessage(`Enter a quantity between 1 and ${available}.`, "error");
        input.focus();
        return;
      }
      await updateCartItem(form.dataset.product, requested);
    });
    form.querySelectorAll("button[data-step]").forEach((button) => button.addEventListener("click", () => {
      const input = form.querySelector('input[name="quantity"]');
      const current = Number(input.value);
      input.value = String(Math.max(1, Math.min(Number(input.max), current + Number(button.dataset.step))));
      form.requestSubmit();
    }));
  });
  document.querySelectorAll(".remove-item").forEach((button) => button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      await removeCartItem(button.dataset.product);
      window.location.reload();
    } catch (error) {
      showMessage(friendlyErrorMessage(error), "error");
      button.disabled = false;
    }
  }));
}

async function updateCartItem(productId, quantity) {
  try {
    await saveCartItem(productId, quantity);
    window.location.reload();
  } catch (error) {
    showMessage(friendlyErrorMessage(error), "error");
  }
}

export async function renderCheckout(user) {
  if (!user) {
    signInToContinue(pageUrl("checkout"));
    return;
  }
  const cart = await getCart();
  if (!cart.items.length) {
    window.location.replace(pageUrl("cart"));
    return;
  }
  document.title = pageTitle("Checkout");
  document.querySelector("#full_name").value = user.full_name;
  document.querySelector("#email").value = user.email;
  document.querySelector("#checkout-summary-items").innerHTML =
    cart.items.map(summaryItem).join("");
  document.querySelector("#checkout-subtotal").textContent = formatPrice(cart.total);
  document.querySelector("#checkout-total").textContent = formatPrice(cart.total);
  document.querySelector("#checkout-unavailable").hidden = !cart.unavailable;
  document.querySelector("#place-order").disabled = cart.unavailable;
  document.querySelector("#checkout-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = event.currentTarget.querySelector('button[type="submit"]');
    button.disabled = true;
    try {
      const order = await placeOrder(Object.fromEntries(new FormData(event.currentTarget)));
      window.location.assign(pageUrl("orderSuccess", { id: order.id }));
    } catch (error) {
      showMessage(friendlyErrorMessage(error), "error");
      button.disabled = false;
    }
  });
}

export async function renderOrders(user) {
  if (!user) {
    signInToContinue(pageUrl("orders"));
    return;
  }
  const orders = await getOrders();
  document.title = pageTitle("My orders");
  document.querySelector("#orders-table").hidden = orders.length === 0;
  document.querySelector("#orders-empty").hidden = orders.length !== 0;
  document.querySelector("#orders-list").innerHTML = orders.map((order) => `<tr>
    <td class="cell-ref" data-label="Order"><a href="${pageUrl("order", { id: order.id })}">Order #${order.id}</a></td>
    <td data-label="Date">${new Date(order.created_at).toLocaleDateString()}</td><td data-label="Items">${order.item_count}</td>
    <td class="cell-status" data-label="Status"><span class="badge ${statusClass(order.status)}">${escapeHtml(order.status_display)}</span></td>
    <td class="cell-total" data-label="Total">${formatPrice(order.total_amount)}</td><td class="cell-action"><a class="btn btn--secondary btn--sm" href="${pageUrl("order", { id: order.id })}">View details</a></td>
  </tr>`).join("");
}

export async function renderOrder(user, successful = false) {
  if (!user) {
    signInToContinue(pageUrl(successful ? "home" : "orders"));
    return;
  }
  const id = params().get("id");
  if (!id || !/^\d+$/.test(id)) {
    window.location.replace(pageUrl("orders"));
    return;
  }
  const order = await getOrder(id);
  document.title = pageTitle(successful ? "Order placed" : `Order #${order.id}`);
  if (successful) {
    document.querySelector("#success-order-reference").textContent = `#${order.id}`;
    document.querySelector("#success-order-items").innerHTML = order.items.map(summaryItem).join("");
    document.querySelector("#success-payment").textContent = order.payment_method_display;
    document.querySelector("#success-total").textContent = formatPrice(order.total_amount);
    document.querySelector("#success-order-link").href = pageUrl("order", { id: order.id });
    return;
  }

  document.querySelector("#order-title").textContent = `Order #${order.id}`;
  document.querySelector("#order-date").textContent =
    `Placed ${new Date(order.created_at).toLocaleDateString()}`;
  document.querySelector("#order-items").innerHTML = order.items.map(summaryItem).join("");
  document.querySelector("#order-payment").textContent = order.payment_method_display;
  document.querySelector("#order-total").textContent = formatPrice(order.total_amount);
  const orderStatus = document.querySelector("#order-status");
  orderStatus.className = `badge ${statusClass(order.status)}`;
  orderStatus.textContent = order.status_display;
  document.querySelector("#order-recipient").textContent = order.full_name;
  document.querySelector("#order-address").innerHTML =
    `${escapeHtml(order.address)}<br>${escapeHtml(order.city)} ${escapeHtml(order.postal_code)}`;
  document.querySelector("#order-phone").textContent = order.phone;
  document.querySelector("#order-email").textContent = order.email;
}

function statusClass(status) {
  if (status === "delivered") return "badge--success";
  if (status === "cancelled") return "badge--danger";
  if (status === "pending") return "badge--warning";
  return "badge--info";
}
