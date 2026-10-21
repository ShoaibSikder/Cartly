import { getHomeData } from "../api/store-api.js?v=cartly-auth-20261021";
import { assetUrl, pageTitle, pageUrl } from "../config.js?v=cartly-account-sidebar-20261021";
import {
  bindWishlistButtons,
  escapeHtml,
  formatPrice,
  productImage,
  renderProductCard,
} from "../components/products.js?v=cartly-product-images-20261021-1";
import { populateCategories } from "../components/shell.js?v=cartly-product-images-20261021-1";

export async function renderHome(user) {
  const data = await getHomeData();
  populateCategories(data.categories);
  document.title = pageTitle("Home");
  const featuredImage = document.querySelector("#featured-image");
  const featuredName = document.querySelector("#featured-name");
  const featuredDescription = document.querySelector("#featured-description");
  const featuredPrice = document.querySelector("#featured-price");
  const featuredLink = document.querySelector("#featured-link");
  if (data.featured_product) {
    const detailUrl = pageUrl("product", { slug: data.featured_product.slug });
    featuredImage.href = detailUrl;
    featuredImage.innerHTML = productImage(data.featured_product);
    featuredName.textContent = data.featured_product.name;
    featuredDescription.hidden = true;
    featuredPrice.textContent = formatPrice(data.featured_product.price);
    featuredLink.href = detailUrl;
    featuredLink.textContent = "View product";
  } else {
    document.querySelector("#featured-product").hidden = true;
  }

  const categoryList = document.querySelector("#category-list");
  categoryList.innerHTML = data.categories.length
    ? data.categories.map((category) => `<li><a class="category-tile" href="${pageUrl("products", { category: category.category })}"><span class="art-mini" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="5" width="16" height="14" rx="2"/><path d="M8 5V3h8v2M8 10h8M8 14h5"/></svg></span>${escapeHtml(category.category)}<small>${category.product_count} product${category.product_count === 1 ? "" : "s"}</small></a></li>`).join("")
    : '<li class="text-muted">No categories available.</li>';
  const popularProducts = document.querySelector("#popular-products");
  popularProducts.innerHTML = data.popular_products.length
    ? data.popular_products.map((product) => renderProductCard(product, user)).join("")
    : `<li class="empty-state"><img src="${assetUrl("empty-state.svg")}" alt="" width="128" height="96"><h3>No products yet</h3><p>Please check back soon.</p></li>`;
  document.querySelector("#new-products").innerHTML =
    data.new_products.map((product) => renderProductCard(product, user)).join("");
  bindWishlistButtons(user);
}
