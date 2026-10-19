from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from apps.products.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    cart_items = list(cart)
    return render(request, "pages/cart.html", {
        "page_name": "cart",
        "cart": cart,
        "cart_items": cart_items,
        "unavailable_items": any(
            item["product"].stock <= 0 or item["quantity"] > item["product"].stock
            for item in cart_items
        ),
    })


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 1
    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
    elif product.stock < 1:
        messages.error(request, "This product is currently out of stock.")
    else:
        cart = Cart(request)
        try:
            existing_quantity = int(cart.data.get(str(product.pk), 0))
        except (TypeError, ValueError):
            existing_quantity = 0
        quantity = min(quantity, max(0, product.stock - existing_quantity))
        if quantity <= 0:
            messages.error(request, "Your cart already contains the available stock for this product.")
        else:
            cart.add(product, quantity=quantity)
            messages.success(request, f"{product.name} was added to your cart.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("cart:detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 0
    cart = Cart(request)
    if quantity <= 0:
        cart.remove(product)
        messages.info(request, "Product removed from your cart.")
    elif product.stock <= 0:
        cart.remove(product)
        messages.error(request, "This product is out of stock and was removed.")
    else:
        cart.add(product, quantity=min(quantity, product.stock), override=True)
        messages.success(request, "Cart updated.")
    return redirect("cart:detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).remove(product)
    messages.info(request, "Product removed from your cart.")
    return redirect("cart:detail")
