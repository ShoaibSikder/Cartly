from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include(("apps.api.urls", "api"), namespace="api"),
    ),
    path(
        "",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/index.html",
            permanent=False,
        ),
        name="home",
    ),
    path("products/", include("apps.products.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("wishlist/", include("apps.wishlists.urls")),
    path("reviews/", include("apps.reviews.urls")),
]

admin.site.site_header = "Cartly system administration"
admin.site.site_title = "Cartly Admin"
admin.site.index_title = "Manage the Cartly store"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
