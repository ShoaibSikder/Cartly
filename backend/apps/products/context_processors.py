from .models import Product


def store_navigation(request):
    categories = (
        Product.objects.filter(is_active=True)
        .exclude(category="")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )
    return {"store_categories": categories}
