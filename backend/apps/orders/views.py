from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from apps.products.models import Product
from apps.cart.cart import Cart
from .forms import CheckoutForm
from .models import Order, OrderItem


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)
    if not cart_items:
        messages.info(request, "Your cart is empty.")
        return redirect("products:product_list")

    initial = {
        "full_name": request.user.get_full_name() or request.user.username,
        "email": request.user.email,
    }
    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = request.user
                order.payment_method = Order.PaymentMethod.COD
                order.status = Order.Status.PENDING
                order.total_amount = Decimal("0.00")
                order.save()

                total = Decimal("0.00")
                for item in cart_items:
                    # Lock each current product row and validate stock again
                    # inside the transaction before reducing inventory.
                    product = Product.objects.select_for_update().filter(
                        pk=item["product"].pk, is_active=True
                    ).first()
                    if product is None:
                        raise ValueError("A product in your cart is no longer available.")
                    quantity = item["quantity"]
                    if quantity > product.stock:
                        raise ValueError(
                            f"Only {product.stock} unit(s) of {product.name} remain. Please update your cart."
                        )
                    unit_price = product.price
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=quantity,
                        price_at_purchase=unit_price,
                    )
                    product.stock -= quantity
                    product.save(update_fields=["stock", "updated_at"])
                    total += unit_price * quantity

                order.total_amount = total
                order.save(update_fields=["total_amount", "updated_at"])
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("cart:detail")

        cart.clear()
        messages.success(request, f"Your order #{order.pk} has been placed.")
        return redirect("orders:success", order_id=order.pk)

    return render(request, "pages/checkout.html", {
        "page_name": "checkout",
        "form": form,
        "cart": cart,
        "cart_items": cart_items,
        "cart_total": cart.total,
    })


@login_required
def success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )
    return render(request, "pages/order_success.html", {
        "order": order,
        "page_name": "order-success",
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related(
        "items",
        "items__product",
    )
    return render(request, "pages/orders.html", {
        "orders": orders,
        "page_name": "orders",
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items", "items__product"),
        pk=order_id,
        user=request.user,
    )
    return render(request, "pages/order.html", {
        "order": order,
        "page_name": "order",
    })
