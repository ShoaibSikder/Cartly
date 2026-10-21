from django.urls import path
from django.conf import settings
from django.views.generic import RedirectView
from . import views

app_name = "wishlists"

urlpatterns = [
    path(
        "",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/wishlist.html",
            permanent=False,
        ),
        name="detail",
    ),
    path("toggle/<int:product_id>/", views.wishlist_toggle, name="toggle"),
]
