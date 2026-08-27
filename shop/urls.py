from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("inventory/", views.inventory, name="inventory"),
    path("inventory/add/", views.add_product, name="add_product"),
    path("inventory/edit/", views.edit_product, name="edit_product"),
    path("inventory/delete/", views.delete_product, name="delete_product"),

    path("product/<int:id>/", views.product_detail, name="product_detail"),

    path("mobile/", views.mobile, name="mobile"),
    path("laptop/", views.laptop, name="laptop"),
    path("headphones/", views.headphones, name="headphones"),
    path("smart/", views.smart, name="smart"),
    path("checkout/", views.checkout, name="checkout"),
    path("cart/", views.cart, name="cart"),
    path("contact/", views.contact, name="contact"),
]
