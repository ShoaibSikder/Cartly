from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("csrf/", views.CsrfTokenView.as_view(), name="csrf"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/me/", views.CurrentUserView.as_view(), name="current-user"),
    path("auth/profile/", views.ProfileView.as_view(), name="profile"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product"),
    path("products/<slug:slug>/reviews/", views.ProductReviewsView.as_view(), name="reviews"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/items/<int:product_id>/", views.CartItemView.as_view(), name="cart-item"),
    path("wishlist/", views.WishlistView.as_view(), name="wishlist"),
    path("wishlist/items/<int:product_id>/", views.WishlistItemView.as_view(), name="wishlist-item"),
    path("orders/", views.OrderListCreateView.as_view(), name="orders"),
    path("orders/<int:order_id>/", views.OrderDetailView.as_view(), name="order"),
]
