from django.contrib import admin

from .models import Delivery, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity")


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


class DeliveryInline(admin.StackedInline):
    model = Delivery
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline, PaymentInline, DeliveryInline]
