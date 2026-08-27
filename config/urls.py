from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from shop import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Authentication
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Home: keep both names because existing templates use both aliases.
    path("", views.home, name="index"),
    path("", views.home, name="home"),

    # Inventory
    path("inventory/", views.inventory, name="inventory"),
    path("inventory/category/<slug:category>/", views.inventory, name="inventory_category"),
    path("customers/", views.customer_master, name="customer_master"),
    path("backup-restore/", views.backup_restore, name="backup_restore"),
    path("backup-restore/download/", views.download_backup, name="download_backup"),
    path("customers/add-sale/", views.add_sale, name="add_sale"),
    path("invoice/<int:id>/", views.invoice, name="invoice"),
    path("invoice/<int:id>/pdf/", views.invoice_pdf, name="invoice_pdf"),

    # Add Product
    path(
        "inventory/add/",
        views.add_product,
        name="add_product"
    ),

    # Edit Product
    path(
        "inventory/edit/<int:id>/",
        views.edit_product,
        name="edit_product"
    ),

    # Delete Product
    path(
        "inventory/delete/<int:id>/",
        views.delete_product,
        name="delete_product"
    ),

    # Product Detail
    path(
        "product/<int:id>/",
        views.product_detail,
        name="product_detail"
    ),

    # Categories
    path(
        "category/<str:category>/",
        views.category_products,
        name="category_products"
    ),

    # Main Pages
    path("mobile/", views.mobile, name="mobile"),
    path("laptops/", views.laptop, name="laptops"),
    path("headphones/", views.headphones, name="headphones"),
    path("smart/", views.smart, name="smart"),
    path("checkout/", views.checkout, name="checkout"),
    path("cart/", views.cart, name="cart"),
    path("orders/place/", views.place_order, name="place_order"),
    path("orders/notifications/", views.order_notifications, name="order_notifications"),
    path("orders/<int:id>/notification/", views.order_notification, name="order_notification"),
    path("contact/", views.contact, name="contact"),
]


# Product image serving
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
