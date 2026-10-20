from django.contrib import admin
from .models import Order, OrderItem


@admin.action(description="Mark selected orders as confirmed")
def mark_confirmed(modeladmin, request, queryset):
    queryset.update(status=Order.Status.CONFIRMED)


@admin.action(description="Mark selected orders as processing")
def mark_processing(modeladmin, request, queryset):
    queryset.update(status=Order.Status.PROCESSING)


@admin.action(description="Mark selected orders as shipped")
def mark_shipped(modeladmin, request, queryset):
    queryset.update(status=Order.Status.SHIPPED)


@admin.action(description="Mark selected orders as delivered")
def mark_delivered(modeladmin, request, queryset):
    queryset.update(status=Order.Status.DELIVERED)


@admin.action(description="Cancel selected orders")
def mark_cancelled(modeladmin, request, queryset):
    queryset.update(status=Order.Status.CANCELLED)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "total_amount", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("id", "user__username", "full_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)
    inlines = [OrderItemInline]
    actions = (
        mark_confirmed,
        mark_processing,
        mark_shipped,
        mark_delivered,
        mark_cancelled,
    )
