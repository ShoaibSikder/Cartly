from decimal import Decimal
from apps.products.models import Product

SESSION_KEY = "cart"


class Cart:
    """Session cart storing product IDs and quantities, never trusted prices."""

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get(SESSION_KEY, {})
        if not isinstance(self.data, dict):
            self.data = {}
            self.session[SESSION_KEY] = self.data

    def add(self, product, quantity=1, override=False):
        product_id = str(product.pk)
        current = self.data.get(product_id, 0)
        try:
            current = int(current)
        except (TypeError, ValueError):
            current = 0
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1
        quantity = max(1, quantity)
        self.data[product_id] = quantity if override else current + quantity
        self.session[SESSION_KEY] = self.data
        self.session.modified = True

    def remove(self, product):
        self.data.pop(str(product.pk), None)
        self.session[SESSION_KEY] = self.data
        self.session.modified = True

    def clear(self):
        self.session.pop(SESSION_KEY, None)
        self.data = {}
        self.session.modified = True

    def __iter__(self):
        ids = []
        for product_id in self.data.keys():
            try:
                ids.append(int(product_id))
            except (TypeError, ValueError):
                continue
        products = Product.objects.filter(pk__in=ids, is_active=True)
        product_map = {str(p.pk): p for p in products}
        for product_id, raw_quantity in list(self.data.items()):
            product = product_map.get(str(product_id))
            if not product:
                continue
            try:
                quantity = max(1, int(raw_quantity))
            except (TypeError, ValueError):
                continue
            yield {
                "product": product,
                "quantity": quantity,
                "unit_price": product.price,
                "total_price": product.price * quantity,
            }

    def __len__(self):
        total = 0
        for item in self:
            total += item["quantity"]
        return total

    @property
    def total(self):
        return sum((item["total_price"] for item in self), Decimal("0.00"))
