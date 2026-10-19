from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from apps.products.models import Product


class CartTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Mug", description="Mug", price=Decimal("250.00"), stock=4
        )

    def test_add_to_cart(self):
        response = self.client.post(reverse("cart:add", args=[self.product.pk]), {"quantity": 2})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["cart"][str(self.product.pk)]), 2)

    def test_cart_add_requires_post(self):
        response = self.client.get(reverse("cart:add", args=[self.product.pk]))
        self.assertEqual(response.status_code, 405)

    def test_cart_cannot_exceed_available_stock(self):
        response = self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": 99},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 4)

    def test_add_rejects_external_and_backslash_redirects(self):
        for next_url in ("https://attacker.example/", "/\\attacker.example/"):
            with self.subTest(next_url=next_url):
                response = self.client.post(
                    reverse("cart:add", args=[self.product.pk]),
                    {"quantity": 1, "next": next_url},
                )
                self.assertEqual(response["Location"], reverse("cart:detail"))

    def test_cart_uses_current_database_price(self):
        response = self.client.post(
            reverse("api:cart-item", args=[self.product.pk]),
            '{"quantity":2,"price":"0.01"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.product.price = Decimal("300.00")
        self.product.save()
        response = self.client.get(reverse("api:cart"))
        self.assertEqual(Decimal(str(response.json()["total"])), Decimal("600.00"))

    def test_cart_blocks_checkout_when_stock_is_no_longer_available(self):
        self.client.post(reverse("cart:add", args=[self.product.pk]), {"quantity": 3})
        self.product.stock = 2
        self.product.save()

        response = self.client.get(reverse("api:cart"))

        self.assertTrue(response.json()["unavailable"])
        self.assertEqual(response.json()["items"][0]["product"]["stock"], 2)
