from django.contrib import admin

from .models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "product__name")
    autocomplete_fields = ("user", "product")
    readonly_fields = ("created_at",)
