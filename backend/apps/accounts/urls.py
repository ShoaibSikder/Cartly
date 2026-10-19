from django.urls import path
from django.conf import settings
from django.views.generic import RedirectView
from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "register/",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/register.html",
            query_string=True,
            permanent=False,
        ),
        name="register",
    ),
    path(
        "login/",
        RedirectView.as_view(
            url=f"{settings.STATIC_URL.rstrip('/')}/pages/login.html",
            query_string=True,
            permanent=False,
        ),
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
