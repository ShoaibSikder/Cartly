from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .forms import ProfileForm


def auth_overlay_redirect(request, mode):
    if mode not in {"login", "register"}:
        raise ValueError(f"Unsupported account overlay mode: {mode}")

    query = request.GET.copy()
    query["account"] = mode
    destination = f"{settings.STATIC_URL.rstrip('/')}/index.html?{query.urlencode()}"
    return redirect(destination)


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
