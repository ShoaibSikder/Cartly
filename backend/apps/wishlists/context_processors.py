from .models import WishlistItem


def wishlist_summary(request):
    if not request.user.is_authenticated:
        return {"wishlist_count": 0, "wishlisted_product_ids": set()}
    items = WishlistItem.objects.filter(user=request.user)
    return {
        "wishlist_count": items.count(),
        "wishlisted_product_ids": set(items.values_list("product_id", flat=True)),
    }
