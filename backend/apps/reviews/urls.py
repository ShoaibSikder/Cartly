from django.urls import path
from apps.api import views as api_views

app_name = "reviews"

urlpatterns = [
    path("<slug:slug>/", api_views.redirect_reviews_page, name="product_reviews"),
]
