from decimal import Decimal
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Product


class ProductTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Backpack", description="A useful backpack",
            price=Decimal("1200.00"), stock=5, category="Bags",
        )

    def test_product_gets_slug(self):
        self.assertEqual(self.product.slug, "test-backpack")

    def test_product_list_shows_active_product(self):
        response = self.client.get(reverse("api:products"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["name"], "Test Backpack")

    def test_inactive_product_is_not_listed(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(reverse("api:products"))
        self.assertEqual(response.json()["results"], [])

    def test_product_detail_shows_database_price_and_stock(self):
        response = self.client.get(
            reverse("api:product", args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["price"], "1200.00")
        self.assertEqual(response.json()["stock"], 5)

    def test_inactive_product_detail_is_not_public(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(
            reverse("api:product", args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 404)

    def test_legacy_product_list_redirects_to_static_page(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertRedirects(
            response,
            "/static/pages/products.html",
            fetch_redirect_response=False,
        )

    @override_settings(DEBUG=False)
    def test_not_found_uses_custom_cartly_error_page(self):
        response = self.client.get("/missing-page/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
        self.assertContains(response, "Browse products", status_code=404)
