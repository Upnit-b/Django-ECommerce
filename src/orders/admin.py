from django.contrib import admin

from .models import Payment, Order, OrderProduct

# Register your models here.


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ("payment", "user", "product", "quantity",
                       "product_price", "ordered")
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "full_name", "phone_number", "email",
                    "city", "order_total", "tax", "status", "ip", "is_ordered", "created_at"]

    list_filter = ["status", "is_ordered"]
    search_fields = ["order_number", "first_name",
                     "last_name", "phone_number", "email"]

    list_per_page = 20
    inlines = [OrderProductInline]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "payment_id", "payment_method",
                    "amount_paid", "status", "created_at"]


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ["order", "payment", "user", "product", "quantity"]


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
