from django.contrib import admin

from .models import Review


@admin.action(description="Approve selected reviews")
def approve_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Hide selected reviews")
def hide_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "title", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("product__name", "user__username", "user__email", "title", "body")
    autocomplete_fields = ("product", "user")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("is_approved",)
    actions = (approve_reviews, hide_reviews)
