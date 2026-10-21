from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.products.models import Product

from .forms import ReviewForm
from .models import Review


@require_http_methods(["GET", "POST"])
def product_reviews(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if request.method == "POST" and not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    review = None
    if request.user.is_authenticated:
        review = Review.objects.filter(user=request.user, product=product).first()
    form = ReviewForm(request.POST or None, instance=review)

    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.is_approved = False
        review.save()
        messages.success(request, "Your review was submitted and is awaiting administrator approval.")
        return redirect("reviews:product_reviews", slug=product.slug)

    reviews = Review.objects.filter(product=product, is_approved=True).select_related("user")
    average_rating = reviews.aggregate(average=Avg("rating"))["average"]
    return render(request, "pages/reviews.html", {
        "page_name": "reviews",
        "product": product,
        "form": form,
        "reviews": reviews,
        "average_rating": average_rating,
        "own_review": review,
    })
