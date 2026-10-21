from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .models import WishlistItem


@login_required
def wishlist_detail(request):
    items = WishlistItem.objects.filter(
        user=request.user,
        product__is_active=True,
    ).select_related("product")
    return render(request, "pages/wishlist.html", {
        "items": items,
        "page_name": "wishlist",
    })


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product,
    )
    if created:
        messages.success(request, f"{product.name} was added to your wishlist.")
    else:
        item.delete()
        messages.info(request, f"{product.name} was removed from your wishlist.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        return redirect(next_url)
    return redirect(reverse("wishlists:detail"))
