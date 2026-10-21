from decimal import Decimal
from pathlib import Path

from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.orders.models import Order
from apps.products.models import Product


class CartlyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username="api-buyer",
            email="api-buyer@example.com",
            password="A-strong-test-password-832!",
        )
        self.product = Product.objects.create(
            name="API Backpack",
            description="A useful backpack for everyday carry.",
            price=Decimal("1200.00"),
            stock=4,
            category="Bags",
        )

    def csrf_headers(self):
        response = self.client.get(reverse("api:csrf"))
        return {"HTTP_X_CSRFTOKEN": response.data["csrfToken"]}

    def test_authentication_flow_accepts_csrf_from_live_preview_origin(self):
        origin = "http://127.0.0.1:3002"
        csrf = self.client.get(reverse("api:csrf"), HTTP_ORIGIN=origin)

        self.assertEqual(csrf.status_code, 200)
        self.assertEqual(csrf["Cache-Control"], "no-store")
        self.assertIn("csrftoken", self.client.cookies)
        self.assertEqual(csrf["Access-Control-Allow-Origin"], origin)

        registration = self.client.post(
            reverse("api:register"),
            {
                "full_name": "Live Preview Buyer",
                "email": "live-preview-buyer@example.com",
                "password1": "A-strong-test-password-832!",
                "password2": "A-strong-test-password-832!",
            },
            format="json",
            HTTP_ORIGIN=origin,
            HTTP_X_CSRFTOKEN=csrf.data["csrfToken"],
        )

        self.assertEqual(registration.status_code, 201)
        self.assertEqual(registration.data["email"], "live-preview-buyer@example.com")
        current_user = self.client.get(reverse("api:current-user"))
        self.assertEqual(current_user.status_code, 200)
        self.assertEqual(current_user.data["user"]["email"], "live-preview-buyer@example.com")

        self.user.set_password("A-strong-test-password-832!")
        self.user.save(update_fields=["password"])
        login_client = APIClient(enforce_csrf_checks=True)
        login_csrf = login_client.get(reverse("api:csrf"), HTTP_ORIGIN=origin)
        login_response = login_client.post(
            reverse("api:login"),
            {
                "email": self.user.email,
                "password": "A-strong-test-password-832!",
            },
            format="json",
            HTTP_ORIGIN=origin,
            HTTP_X_CSRFTOKEN=login_csrf.data["csrfToken"],
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.data["email"], self.user.email)
        self.assertTrue(login_client.session.get("_auth_user_id"))

    def test_root_redirects_to_static_frontend_entry(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/static/index.html")
        entry = finders.find("index.html")
        self.assertIsNotNone(entry)
        for html_file in Path(entry).parent.rglob("*.html"):
            with html_file.open(encoding="utf-8") as frontend:
                source = frontend.read()
            self.assertNotIn("{{", source, html_file.name)
            self.assertNotIn("{%", source, html_file.name)

    def test_static_pages_own_their_content_and_form_structure(self):
        frontend_root = Path(finders.find("index.html")).parent
        page_markers = {
            "index.html": ("id=\"hero-title\"", "id=\"popular-products\""),
            "pages/products.html": ("id=\"filters-form\"", "id=\"product-list\""),
            "pages/product_detail.html": ("id=\"add-cart-form\"", "id=\"related-products\""),
            "pages/profile.html": ("id=\"profile-form\"", "id=\"profile-order-count\""),
            "pages/cart.html": ("id=\"cart-items\"", "id=\"cart-empty\""),
            "pages/checkout.html": ("id=\"checkout-form\"", "id=\"checkout-summary-items\""),
            "pages/orders.html": ("id=\"orders-table\"", "id=\"orders-empty\""),
            "pages/order.html": ("id=\"order-items\"", "id=\"order-status\""),
            "pages/order_success.html": ("id=\"success-order-items\"", "id=\"success-total\""),
            "pages/wishlist.html": ("id=\"wishlist-grid\"", "id=\"wishlist-empty\""),
            "pages/reviews.html": ("id=\"review-submit\"", "id=\"review-list\""),
        }

        for relative_path, markers in page_markers.items():
            with (frontend_root / relative_path).open(encoding="utf-8") as page:
                source = page.read()
            for marker in markers:
                self.assertIn(marker, source, f"{relative_path} should define {marker}")

    def test_legacy_product_detail_redirects_to_static_page_with_slug(self):
        response = self.client.get(
            reverse("products:product_detail", args=[self.product.slug])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            f"/static/pages/product_detail.html?slug={self.product.slug}",
        )

    def test_product_list_returns_safe_image_url_and_rating_data(self):
        response = self.client.get(reverse("api:products"))

        self.assertEqual(response.status_code, 200)
        product = response.data["results"][0]
        self.assertEqual(product["id"], self.product.pk)
        self.assertIsNone(product["image"])
        self.assertFalse(product["in_wishlist"])
        self.assertEqual(product["price"], "1200.00")

    def test_cart_api_adds_items_and_rejects_quantity_above_stock(self):
        headers = self.csrf_headers()
        added = self.client.post(
            reverse("api:cart-item", args=[self.product.pk]),
            {"quantity": 3},
            format="json",
            **headers,
        )
        rejected = self.client.post(
            reverse("api:cart-item", args=[self.product.pk]),
            {"quantity": 2},
            format="json",
            **headers,
        )
        cart = self.client.get(reverse("api:cart"))

        self.assertEqual(added.status_code, 200)
        self.assertEqual(rejected.status_code, 400)
        self.assertEqual(cart.data["count"], 3)
        self.assertEqual(cart.data["total"], Decimal("3600.00"))

    def test_registration_requires_csrf_and_creates_authenticated_user(self):
        data = {
            "full_name": "API Buyer",
            "email": "new-api-buyer@example.com",
            "password1": "A-strong-test-password-832!",
            "password2": "A-strong-test-password-832!",
        }
        rejected = self.client.post(
            reverse("api:register"),
            data,
            format="json",
        )
        self.assertEqual(rejected.status_code, 403)

        headers = self.csrf_headers()
        created = self.client.post(
            reverse("api:register"),
            data,
            format="json",
            **headers,
        )

        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data["email"], data["email"])
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_profile_requires_login_and_updates_only_current_user(self):
        denied = self.client.get(reverse("api:profile"))
        self.assertEqual(denied.status_code, 403)

        self.client.force_login(self.user)
        updated = self.client.patch(
            reverse("api:profile"),
            {"first_name": "Cartly", "last_name": "Customer", "email": "new@example.com"},
            format="json",
            **self.csrf_headers(),
        )

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["full_name"], "Cartly Customer")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")

    def test_wishlist_api_is_authenticated_and_product_state_is_exposed(self):
        denied = self.client.get(reverse("api:wishlist"))
        self.assertEqual(denied.status_code, 403)

        self.client.force_login(self.user)
        saved = self.client.post(
            reverse("api:wishlist-item", args=[self.product.pk]),
            format="json",
            **self.csrf_headers(),
        )
        product = self.client.get(
            reverse("api:product", args=[self.product.slug])
        )
        removed = self.client.delete(
            reverse("api:wishlist-item", args=[self.product.pk]),
            **self.csrf_headers(),
        )
        wishlist = self.client.get(reverse("api:wishlist"))

        self.assertEqual(saved.status_code, 200)
        self.assertTrue(product.data["in_wishlist"])
        self.assertEqual(removed.status_code, 200)
        self.assertEqual(wishlist.data, [])

    def test_checkout_rechecks_stock_and_order_access_is_private(self):
        self.client.force_login(self.user)
        headers = self.csrf_headers()
        add_response = self.client.post(
            reverse("api:cart-item", args=[self.product.pk]),
            {"quantity": 2},
            format="json",
            **headers,
        )
        self.assertEqual(add_response.status_code, 200)

        response = self.client.post(
            reverse("api:orders"),
            {
                "full_name": "API Buyer",
                "email": "api-buyer@example.com",
                "phone": "01234567890",
                "address": "1 API Street",
                "city": "Dhaka",
                "postal_code": "1207",
            },
            format="json",
            **headers,
        )

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.total_amount, Decimal("2400.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        other_client = APIClient()
        other = User.objects.create_user(
            username="other-api-buyer",
            password="A-strong-test-password-832!",
        )
        other_client.force_login(other)
        private_order = other_client.get(reverse("api:order", args=[order.pk]))
        self.assertEqual(private_order.status_code, 404)

    def test_checkout_rejects_stock_changes_without_creating_an_order(self):
        self.client.force_login(self.user)
        added = self.client.post(
            reverse("api:cart-item", args=[self.product.pk]),
            {"quantity": 3},
            format="json",
            **self.csrf_headers(),
        )
        self.assertEqual(added.status_code, 200)
        self.product.stock = 2
        self.product.save()

        response = self.client.post(
            reverse("api:orders"),
            {
                "full_name": "API Buyer",
                "email": "api-buyer@example.com",
                "phone": "01234567890",
                "address": "1 API Street",
                "city": "Dhaka",
            },
            format="json",
            **self.csrf_headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.filter(user=self.user).exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)
