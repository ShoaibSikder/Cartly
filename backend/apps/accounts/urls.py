from django.urls import path
from django.conf import settings
from django.views.generic import RedirectView
from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "register/",
        views.auth_overlay_redirect,
        {"mode": "register"},
        name="register",
    ),
    path(
        "login/",
        views.auth_overlay_redirect,
        {"mode": "login"},
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path(
        "profile/",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/profile.html",
            permanent=False,
        ),
        name="profile",
    ),
]
