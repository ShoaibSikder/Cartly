from django.urls import path
from django.conf import settings
from django.views.generic import RedirectView
from apps.api import views as api_views

app_name = "orders"

urlpatterns = [
    path(
        "checkout/",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/checkout.html",
            permanent=False,
        ),
        name="checkout",
    ),
    path("success/<int:order_id>/", api_views.redirect_order_success_page, name="success"),
    path(
        "history/",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/orders.html",
            permanent=False,
        ),
        name="history",
    ),
    path("<int:order_id>/", api_views.redirect_order_page, name="detail"),
]
