from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.reviews.models import Review
from apps.wishlists.models import WishlistItem

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    in_wishlist = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True, allow_null=True)
    review_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "price",
            "stock",
            "image",
            "in_wishlist",
            "category",
            "average_rating",
            "review_count",
        )

    def get_image(self, product):
        if not product.image or not product.image.storage.exists(product.image.name):
            return None

        request = self.context.get("request")
        image_url = product.image.url
        if request is not None:
            return request.build_absolute_uri(image_url)
        return image_url

    def get_in_wishlist(self, product):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and WishlistItem.objects.filter(
                user=request.user,
                product=product,
            ).exists()
        )


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "full_name")

    def get_full_name(self, user):
        return user.get_full_name()


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("id", "rating", "title", "body", "user_name", "created_at")

    def get_user_name(self, review):
        return review.user.get_full_name() or review.user.username


class CartItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2)


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "quantity",
            "price_at_purchase",
            "line_total",
            "image",
        )

    def get_image(self, item):
        image = item.product.image
        if not image or not image.storage.exists(image.name):
            return None

        request = self.context.get("request")
        image_url = image.url
        return request.build_absolute_uri(image_url) if request else image_url


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(
        source="get_payment_method_display",
        read_only=True,
    )
    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "status",
            "status_display",
            "payment_method",
            "payment_method_display",
            "total_amount",
            "item_count",
            "created_at",
            "items",
        )
