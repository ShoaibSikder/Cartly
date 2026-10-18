from django.urls import path
from django.conf import settings
from django.views.generic import RedirectView
from apps.api import views as api_views

app_name = "products"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/products.html",
            query_string=True,
            permanent=False,
        ),
        name="product_list",
    ),
    path("<slug:slug>/", api_views.redirect_product_page, name="product_detail"),
]
