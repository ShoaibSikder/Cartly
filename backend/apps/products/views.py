from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render
from apps.reviews.models import Review
from apps.wishlists.models import WishlistItem
from .models import Product


def _reviewed_products():
    return Product.objects.annotate(
        average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
        review_count=Count("reviews", filter=Q(reviews__is_approved=True)),
    )


def _decimal_param(value):
    if not value:
        return None
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None
    return amount if amount.is_finite() and amount >= 0 else None


def home(request):
    products = _reviewed_products().filter(is_active=True)
    categories = (
        Product.objects.filter(is_active=True)
        .exclude(category="")
        .values("category")
        .annotate(product_count=Count("pk"))
        .order_by("category")
    )
    popular_products = products.order_by("-review_count", "-created_at")[:4]
    return render(request, "index.html", {
        "page_name": "home",
        "featured_product": products.order_by("-created_at").first(),
        "categories": categories,
        "popular_products": popular_products,
        "new_products": products.order_by("-created_at")[:4],
    })


def product_list(request):
    products = _reviewed_products().filter(is_active=True)
    query = request.GET.get("q", "").strip()
    selected_categories = [value.strip() for value in request.GET.getlist("category") if value.strip()]

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
    if selected_categories:
        products = products.filter(category__in=selected_categories)

    min_price = _decimal_param(request.GET.get("min"))
    max_price = _decimal_param(request.GET.get("max"))
    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)
    in_stock = request.GET.get("stock") == "1"
    if in_stock:
        products = products.filter(stock__gt=0)

    ordering = {
        "newest": "-created_at",
        "price-asc": "price",
        "price-desc": "-price",
        "rating": "-average_rating",
    }.get(request.GET.get("sort"), "-created_at")
    products = products.order_by(ordering, "pk")

    categories = (
        Product.objects.filter(is_active=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(request, "pages/products.html", {
        "page_name": "products",
        "products": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "selected_categories": selected_categories,
        "min_price": request.GET.get("min", ""),
        "max_price": request.GET.get("max", ""),
        "in_stock": in_stock,
        "sort": request.GET.get("sort", "featured"),
        "categories": categories,
        "query_params": query_params.urlencode(),
        "result_count": paginator.count,
        "catalogue_title": (
            f"Results for “{query}”" if query
            else selected_categories[0] if len(selected_categories) == 1
            else "All products"
        ),
    })


def product_detail(request, slug):
    product = get_object_or_404(
        _reviewed_products(),
        slug=slug,
        is_active=True,
    )
    approved_reviews = Review.objects.filter(
        product=product,
        is_approved=True,
    ).select_related("user")
    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(
            user=request.user,
            product=product,
        ).exists()
    else:
        in_wishlist = False
    return render(request, "pages/product_detail.html", {
        "page_name": "product",
        "product": product,
        "approved_reviews": approved_reviews[:4],
        "related_products": _reviewed_products().filter(
            is_active=True,
            category=product.category,
        ).exclude(pk=product.pk).order_by("-created_at")[:4],
        "in_wishlist": in_wishlist,
    })
