from decimal import Decimal
from io import StringIO
from django.core.management import call_command
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

    def test_sample_catalog_command_creates_products_and_is_idempotent(self):
        call_command("seed_sample_products", stdout=StringIO())

        products = Product.objects.filter(
            slug__in=(
                "stoneware-coffee-set",
                "linen-cushion-cover",
                "arc-desk-lamp",
                "wireless-studio-headphones",
                "everyday-canvas-tote",
                "insulated-steel-bottle",
            )
        )
        self.assertEqual(products.count(), 6)
        self.assertSetEqual(
            set(products.values_list("category", flat=True)),
            {"Home & Living", "Electronics", "Accessories"},
        )
        self.assertTrue(all(product.image.storage.exists(product.image.name) for product in products))
        self.assertTrue(all(product.image.name.endswith(".png") for product in products))

        call_command("seed_sample_products", stdout=StringIO())
        self.assertEqual(products.count(), 6)

    def test_sample_catalog_command_updates_existing_product_svg_to_png(self):
        product = Product.objects.create(
            name="Stoneware Coffee Set",
            slug="stoneware-coffee-set",
            description="Existing sample product",
            price=Decimal("1450.00"),
            stock=18,
            category="Home & Living",
            image="products/stoneware-coffee-set.svg",
        )

        call_command("seed_sample_products", stdout=StringIO())

        product.refresh_from_db()
        self.assertEqual(product.image.name, "products/stoneware-coffee-set.png")

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
