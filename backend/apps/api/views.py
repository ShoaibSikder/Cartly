from decimal import Decimal, InvalidOperation

from django.contrib.auth import login, logout
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils.decorators import decorator_from_middleware, method_decorator
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.forms import (
    EmailAuthenticationForm,
    ProfileForm,
    RegistrationForm,
)
from apps.api.middleware import LocalDevelopmentCsrfViewMiddleware
from apps.cart.cart import Cart
from apps.orders.forms import CheckoutForm
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.reviews.forms import ReviewForm
from apps.reviews.models import Review
from apps.wishlists.models import WishlistItem

from .serializers import (
    CartItemSerializer,
    OrderSerializer,
    ProductSerializer,
    ReviewSerializer,
    UserSerializer,
)

csrf_protect_local = decorator_from_middleware(LocalDevelopmentCsrfViewMiddleware)


def csrf_failure(request, reason=""):
    if request.path.startswith("/api/"):
        return JsonResponse(
            {
                "detail": (
                    "CSRF verification failed. Refresh the page and try again. "
                    "If this continues, add the frontend origin to "
                    "CSRF_TRUSTED_ORIGINS and CORS_ALLOWED_ORIGINS."
                ),
                "reason": reason,
            },
            status=403,
        )
    from django.views.csrf import csrf_failure as default_csrf_failure

    return default_csrf_failure(request, reason=reason)


def products_with_ratings():
    return Product.objects.annotate(
        average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
        review_count=Count("reviews", filter=Q(reviews__is_approved=True)),
    )


def api_form_errors(form):
    return serializers.ValidationError(form.errors.get_json_data())


def serialized_products(products, request):
    return ProductSerializer(
        products,
        many=True,
        context={"request": request},
    ).data


def cart_payload(request):
    cart = Cart(request)
    items = list(cart)
    product_ids = [item["product"].pk for item in items]
    products = {
        product.pk: product
        for product in products_with_ratings().filter(pk__in=product_ids)
    }
    items = [
        {**item, "product": products[item["product"].pk]}
        for item in items
        if item["product"].pk in products
    ]

    return {
        "items": CartItemSerializer(
            items,
            many=True,
            context={"request": request},
        ).data,
        "count": len(cart),
        "total": cart.total,
        "unavailable": any(
            item["quantity"] > item["product"].stock
            or item["product"].stock <= 0
            for item in items
        ),
    }


class CsrfTokenView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        response = Response({"csrfToken": get_token(request)})
        response["Cache-Control"] = "no-store"
        return response


@method_decorator(csrf_protect_local, name="dispatch")
class RegisterView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        form = RegistrationForm(data=request.data)
        if not form.is_valid():
            raise api_form_errors(form)

        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_protect_local, name="dispatch")
class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        form = EmailAuthenticationForm(request, data=request.data)
        if not form.is_valid():
            raise api_form_errors(form)

        user = form.get_user()
        login(request, user)
        return Response(UserSerializer(user).data)


@method_decorator(csrf_protect_local, name="dispatch")
class LogoutView(APIView):
    # DRF's SessionAuthentication runs its own default CSRF check before the
    # view. That check does not use our local-development origin policy, so a
    # separate local frontend can be rejected even after this view's CSRF
    # decorator accepts the request.
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"user": None})
        return Response({"user": UserSerializer(request.user).data})


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        form = ProfileForm(data=request.data, instance=request.user)
        if not form.is_valid():
            raise api_form_errors(form)
        user = form.save()
        return Response(UserSerializer(user).data)


class HomeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        products = products_with_ratings().filter(is_active=True)
        categories = list(
            Product.objects.filter(is_active=True)
            .exclude(category="")
            .values("category")
            .annotate(product_count=Count("pk"))
            .order_by("category")
        )
        featured_product = products.order_by("-created_at").first()
        popular_products = products.order_by("-review_count", "-created_at")[:4]
        new_products = products.order_by("-created_at")[:4]

        return Response({
            "featured_product": (
                ProductSerializer(featured_product, context={"request": request}).data
                if featured_product else None
            ),
            "categories": categories,
            "popular_products": serialized_products(popular_products, request),
            "new_products": serialized_products(new_products, request),
        })


class ProductListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        products = products_with_ratings().filter(is_active=True)
        query = request.query_params.get("q", "").strip()
        if query:
            products = products.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(category__icontains=query)
            )

        categories = [
            value.strip()
            for value in request.query_params.getlist("category")
            if value.strip()
        ]
        if categories:
            products = products.filter(category__in=categories)

        for key, lookup in (("min", "price__gte"), ("max", "price__lte")):
            value = request.query_params.get(key)
            if value:
                try:
                    price = Decimal(value)
                except (InvalidOperation, TypeError, ValueError):
                    continue
                if price.is_finite() and price >= 0:
                    products = products.filter(**{lookup: price})

        in_stock = request.query_params.get("stock") == "1"
        if in_stock:
            products = products.filter(stock__gt=0)

        ordering = {
            "newest": "-created_at",
            "price-asc": "price",
            "price-desc": "-price",
            "rating": "-average_rating",
        }.get(request.query_params.get("sort"), "-created_at")
        products = products.order_by(ordering, "pk")

        categories = list(
            Product.objects.filter(is_active=True)
            .exclude(category="")
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )
        paginator = Paginator(products, 9)
        page = paginator.get_page(request.query_params.get("page"))
        return Response({
            "results": serialized_products(page.object_list, request),
            "count": paginator.count,
            "page": page.number,
            "total_pages": paginator.num_pages,
            "categories": categories,
        })


class ProductDetailView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, slug):
        product = get_object_or_404(
            products_with_ratings(),
            slug=slug,
            is_active=True,
        )
        data = ProductSerializer(product, context={"request": request}).data
        data["related_products"] = serialized_products(
            products_with_ratings()
            .filter(is_active=True, category=product.category)
            .exclude(pk=product.pk)
            .order_by("-created_at")[:4],
            request,
        )
        return Response(data)


class ProductReviewsView(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (JSONParser, FormParser, MultiPartParser)

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        approved_reviews = Review.objects.filter(
            product=product,
            is_approved=True,
        ).select_related("user")
        result = {
            "average_rating": approved_reviews.aggregate(
                average=Avg("rating")
            )["average"],
            "review_count": approved_reviews.count(),
            "reviews": ReviewSerializer(approved_reviews, many=True).data,
            "my_review": None,
        }
        if request.user.is_authenticated:
            own_review = Review.objects.filter(
                product=product,
                user=request.user,
            ).first()
            if own_review:
                result["my_review"] = {
                    **ReviewSerializer(own_review).data,
                    "is_approved": own_review.is_approved,
                }
        return Response(result)

    def post(self, request, slug):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Sign in to submit a review."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        product = get_object_or_404(Product, slug=slug, is_active=True)
        review = Review.objects.filter(user=request.user, product=product).first()
        form = ReviewForm(data=request.data, instance=review)
        if not form.is_valid():
            raise api_form_errors(form)

        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.is_approved = False
        review.save()
        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


class CartView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(cart_payload(request))


class CartItemView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        quantity = serializers.IntegerField(min_value=1).run_validation(
            request.data.get("quantity", 1)
        )
        cart = Cart(request)
        try:
            current_quantity = max(0, int(cart.data.get(str(product.pk), 0)))
        except (TypeError, ValueError):
            current_quantity = 0
        available = product.stock - current_quantity
        if available <= 0:
            raise serializers.ValidationError({
                "quantity": "Your cart already contains the available stock."
            })
        if quantity > available:
            raise serializers.ValidationError({
                "quantity": f"Only {available} unit(s) can be added."
            })
        cart.add(product, quantity=quantity)
        return Response(cart_payload(request))

    def put(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        quantity = serializers.IntegerField(min_value=0).run_validation(
            request.data.get("quantity")
        )
        cart = Cart(request)
        if quantity == 0:
            cart.remove(product)
            return Response(cart_payload(request))
        if quantity > product.stock:
            raise serializers.ValidationError({
                "quantity": f"Only {product.stock} unit(s) are available."
            })
        cart.add(product, quantity=quantity, override=True)
        return Response(cart_payload(request))

    def delete(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        Cart(request).remove(product)
        return Response(cart_payload(request))


class WishlistView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        items = WishlistItem.objects.filter(
            user=request.user,
            product__is_active=True,
        ).select_related("product")
        products = products_with_ratings().filter(
            pk__in=items.values_list("product_id", flat=True)
        )
        return Response(serialized_products(products, request))


class WishlistItemView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        WishlistItem.objects.get_or_create(user=request.user, product=product)
        return Response({"saved": True})

    def delete(self, request, product_id):
        WishlistItem.objects.filter(
            user=request.user,
            product_id=product_id,
        ).delete()
        return Response({"saved": False})


class OrderListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items")
        return Response(OrderSerializer(orders, many=True, context={"request": request}).data)

    def post(self, request):
        cart = Cart(request)
        cart_items = list(cart)
        if not cart_items:
            raise serializers.ValidationError({"cart": "Your cart is empty."})

        form = CheckoutForm(data=request.data)
        if not form.is_valid():
            raise api_form_errors(form)

        with transaction.atomic():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = Decimal("0.00")
            order.save()

            total = Decimal("0.00")
            for item in cart_items:
                product = Product.objects.select_for_update().filter(
                    pk=item["product"].pk,
                    is_active=True,
                ).first()
                if product is None:
                    raise serializers.ValidationError({
                        "cart": "A product in your cart is no longer available."
                    })
                quantity = item["quantity"]
                if quantity > product.stock:
                    raise serializers.ValidationError({
                        "cart": f"Only {product.stock} unit(s) of {product.name} remain."
                    })

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    price_at_purchase=product.price,
                )
                product.stock -= quantity
                product.save(update_fields=("stock", "updated_at"))
                total += product.price * quantity

            order.total_amount = total
            order.save(update_fields=("total_amount", "updated_at"))

        cart.clear()
        order = Order.objects.prefetch_related("items").get(pk=order.pk)
        return Response(
            OrderSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            pk=order_id,
            user=request.user,
        )
        return Response(OrderSerializer(order, context={"request": request}).data)


def frontend_page(page, query=None):
    from django.http import HttpResponseRedirect
    from django.utils.http import urlencode

    url = f"{settings.STATIC_URL.rstrip('/')}/pages/{page}.html"
    if query:
        url = f"{url}?{urlencode(query)}"
    return HttpResponseRedirect(url)


def redirect_product_page(request, slug):
    return frontend_page("product_detail", {"slug": slug})


def redirect_order_page(request, order_id):
    return frontend_page("order", {"id": order_id})


def redirect_order_success_page(request, order_id):
    return frontend_page("order_success", {"id": order_id})


def redirect_reviews_page(request, slug):
    return frontend_page("reviews", {"slug": slug})
