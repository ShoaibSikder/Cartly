from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import EmailAuthenticationForm, ProfileForm, RegistrationForm


def _safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def register(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request) or "products:product_list")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your Cartly account has been created.")
        return redirect(_safe_next_url(request) or "products:product_list")
    return render(request, "pages/register.html", {"form": form, "page_name": "register"})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request) or "products:product_list")
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "You are now logged in.")
        return redirect(_safe_next_url(request) or "products:product_list")
    return render(request, "pages/login.html", {"form": form, "page_name": "login"})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("products:product_list")


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile was updated.")
        return redirect("accounts:profile")
    return render(request, "pages/profile.html", {
        "form": form,
        "page_name": "profile",
        "order_count": request.user.orders.count(),
        "wishlist_count": request.user.wishlist_items.count(),
    })
