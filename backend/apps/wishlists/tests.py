from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product

from .models import WishlistItem


class WishlistTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="wishlist-user", password="test-pass-123")
        self.product = Product.objects.create(
            name="Wishlist Backpack",
            description="A useful backpack",
            price="1200.00",
            stock=3,
        )
        self.client.force_login(self.user)

    def test_add_and_remove_product(self):
        url = reverse("wishlists:toggle", args=[self.product.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

    def test_wishlist_is_private(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        other_user = User.objects.create_user(username="other-user", password="test-pass-123")
        self.client.force_login(other_user)
        response = self.client.get(reverse("api:wishlist"))
        self.assertEqual(response.json(), [])

    def test_toggle_requires_login_and_post(self):
        self.client.logout()
        response = self.client.post(reverse("wishlists:toggle", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get(reverse("wishlists:toggle", args=[self.product.pk]))
        self.assertEqual(response.status_code, 405)
