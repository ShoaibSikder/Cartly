import json
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from apps.products.models import Product
from .models import Order, OrderItem


class OrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="Strong-test-password-123!")
        self.product = Product.objects.create(
            name="Test Keyboard", description="Keyboard",
            price=Decimal("1500.00"), stock=5
        )
        self.client.login(username="buyer", password="Strong-test-password-123!")

    def test_checkout_creates_order_and_reduces_stock(self):
        self.client.post(reverse("cart:add", args=[self.product.pk]), {"quantity": 2})
        response = self.client.post(reverse("api:orders"), json.dumps({
            "full_name": "Test Buyer",
            "email": "buyer@example.com",
            "phone": "01234567890",
            "address": "1 Test Street",
            "city": "Dhaka",
            "postal_code": "1207",
        }), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_amount, Decimal("3000.00"))
        self.assertEqual(order.items.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_order_is_private_to_owner(self):
        order = Order.objects.create(
            user=self.user, full_name="Buyer", email="buyer@example.com",
            phone="0123", address="Street", city="Dhaka",
            total_amount=Decimal("0.00")
        )
        other = User.objects.create_user(username="other", password="Another-strong-password-123!")
        self.client.logout()
        self.client.login(username="other", password="Another-strong-password-123!")
        response = self.client.get(reverse("api:order", args=[order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_view_order_history_and_order_detail(self):
        order = Order.objects.create(
            user=self.user,
            full_name="Buyer",
            email="buyer@example.com",
            phone="0123",
            address="Street",
            city="Dhaka",
            total_amount=Decimal("3000.00"),
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            quantity=2,
            price_at_purchase=self.product.price,
        )

        history = self.client.get(reverse("api:orders"))
        detail = self.client.get(reverse("api:order", args=[order.pk]))

        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.json()[0]["id"], order.pk)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["items"][0]["product_name"], self.product.name)
        self.assertEqual(detail.json()["total_amount"], "3000.00")

    def test_order_history_only_shows_current_users_orders(self):
        other = User.objects.create_user(username="other-buyer", password="test-pass-123")
        Order.objects.create(
            user=other,
            full_name="Other Buyer",
            email="other@example.com",
            phone="0123",
            address="Other Street",
            city="Dhaka",
            total_amount=Decimal("10.00"),
        )
        response = self.client.get(reverse("api:orders"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
