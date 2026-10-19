from django.urls import path
from django.conf import settings
from django.views.generic import RedirectView
from . import views

app_name = "cart"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/cart.html",
            permanent=False,
        ),
        name="detail",
    ),
    path("add/<int:product_id>/", views.cart_add, name="add"),
    path("update/<int:product_id>/", views.cart_update, name="update"),
    path("remove/<int:product_id>/", views.cart_remove, name="remove"),
]
