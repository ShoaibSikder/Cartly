from .cart import Cart


def cart_summary(request):
    cart = Cart(request)
    return {"cart_count": len(cart)}
