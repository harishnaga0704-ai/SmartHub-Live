from django.contrib import admin
from .models import Customer, Product, ProductImage, Order


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address", "created_at", "updated_at")
    search_fields = ("name", "email", "phone")
    readonly_fields = ("created_at", "updated_at")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "offer_price", "stock")
    list_filter = ("category",)
    search_fields = ("name", "brand")
    inlines = (ProductImageInline,)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "customer_name", "product", "quantity", "total",
        "payment_method", "status", "created",
    )
    list_filter = ("status", "payment_method", "created")
    search_fields = ("customer_name", "email", "phone", "product__name")
    readonly_fields = ("created", "created_at", "total")
    list_select_related = ("product", "customer")
    ordering = ("-created",)
