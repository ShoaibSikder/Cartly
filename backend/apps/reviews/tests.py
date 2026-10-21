from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product

from .models import Review


class ReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="review-user", password="test-pass-123")
        self.product = Product.objects.create(
            name="Reviewed Keyboard",
            description="A keyboard",
            price="1500.00",
            stock=2,
        )
        self.client.force_login(self.user)
        self.url = reverse("api:reviews", args=[self.product.slug])

    def test_review_is_unpublished_until_approved(self):
        response = self.client.post(self.url, {
            "rating": 5,
            "title": "Excellent",
            "body": "Works very well.",
        })
        self.assertEqual(response.status_code, 201)
        review = Review.objects.get(user=self.user, product=self.product)
        self.assertFalse(review.is_approved)

    def test_users_cannot_create_duplicate_reviews(self):
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            title="Original",
            body="Original review.",
        )
        response = self.client.post(self.url, {
            "rating": 3,
            "title": "Updated",
            "body": "Updated review.",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.filter(user=self.user, product=self.product).count(), 1)
        self.assertEqual(Review.objects.get(user=self.user, product=self.product).title, "Updated")

    def test_unapproved_reviews_are_excluded_from_approved_review_list(self):
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=1,
            title="Pending review",
            body="Awaiting moderation.",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.json()["reviews"], [])
        self.assertFalse(response.json()["my_review"]["is_approved"])

    def test_reviews_are_readable_without_an_account(self):
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            title="Public review",
            body="Approved and visible.",
            is_approved=True,
        )
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reviews"][0]["body"], "Approved and visible.")

    def test_review_submission_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url, {
            "rating": 5,
            "title": "Review",
            "body": "Sign-in required.",
        })
        self.assertEqual(response.status_code, 401)
        self.assertFalse(Review.objects.exists())

    def test_rating_outside_range_is_rejected(self):
        response = self.client.post(self.url, {
            "rating": 6,
            "title": "Invalid",
            "body": "Invalid rating.",
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Review.objects.filter(user=self.user, product=self.product).exists())
