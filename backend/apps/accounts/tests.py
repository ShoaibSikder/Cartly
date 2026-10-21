from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_account_routes_open_header_overlay_and_preserve_next_url(self):
        next_url = "/static/pages/cart.html"
        for route, mode in (("accounts:login", "login"), ("accounts:register", "register")):
            with self.subTest(mode=mode):
                response = self.client.get(reverse(route), {"next": next_url})
                location = urlsplit(response["Location"])

                self.assertEqual(response.status_code, 302)
                self.assertEqual(location.path, "/static/index.html")
                self.assertEqual(
                    parse_qs(location.query),
                    {"next": [next_url], "account": [mode]},
                )

    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(reverse("api:register"), {
            "username": "cartlyuser",
            "full_name": "Cartly User",
            "email": "user@example.com",
            "password1": "A-strong-test-password-832!",
            "password2": "A-strong-test-password-832!",
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="cartlyuser").exists())
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_rejects_external_next_url(self):
        User.objects.create_user(
            username="cartlyuser",
            email="user@example.com",
            password="A-strong-test-password-832!",
        )
        response = self.client.post(reverse("api:login") + "?next=https://attacker.example/", {
            "email": "user@example.com",
            "password": "A-strong-test-password-832!",
            "next": "https://attacker.example/",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_accepts_email_and_preserves_safe_next_url(self):
        User.objects.create_user(
            username="cartlyuser",
            email="user@example.com",
            password="A-strong-test-password-832!",
        )
        response = self.client.post(reverse("api:login"), {
            "email": "USER@example.com",
            "password": "A-strong-test-password-832!",
            "next": "/cart/",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "user@example.com")

    def test_registration_requires_full_name_and_preserves_safe_next_url(self):
        response = self.client.post(reverse("api:register"), {
            "email": "user@example.com",
            "full_name": "Cartly User",
            "password1": "A-strong-test-password-832!",
            "password2": "A-strong-test-password-832!",
            "next": "/cart/",
        })
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="user@example.com")
        self.assertEqual(user.get_full_name(), "Cartly User")

    def test_logout_requires_post(self):
        response = self.client.get(reverse("api:logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_clears_authenticated_session(self):
        user = User.objects.create_user(username="logout-user", password="test-pass-123")
        self.client.force_login(user)
        response = self.client.post(reverse("api:logout"))
        self.assertEqual(response.status_code, 204)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(username="existing", email="buyer@example.com", password="test-pass-123")
        response = self.client.post(reverse("api:register"), {
            "username": "new-user",
            "full_name": "New User",
            "email": "BUYER@example.com",
            "password1": "A-strong-test-password-832!",
            "password2": "A-strong-test-password-832!",
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="new-user").exists())
