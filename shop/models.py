from django.conf import settings
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    description = models.TextField(blank=True)
    specifications = models.TextField(blank=True, help_text="Enter one specification per line, for example: Display: 6.7 inch")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    VIEW_CHOICES = [
        ("Front", "Front View"),
        ("Back", "Back View"),
        ("Side", "Side View"),
        ("Size", "Size / Dimensions"),
        ("Other", "Other View"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="detail_images")
    view_name = models.CharField(max_length=20, choices=VIEW_CHOICES, default="Other")
    image = models.ImageField(upload_to="products/details/")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.product.name} - {self.view_name}"


class Customer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="customer_profiles",
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("email", "phone"), name="unique_customer_contact"),
        ]

    def __str__(self):
        return self.name


class Order(models.Model):
    customer_profile = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders"
    )
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, default="COD")
    status = models.CharField(max_length=30, default="Completed")
    is_seen = models.BooleanField(default=False)
    # This column already exists in the production MySQL table from an earlier schema.
    created_at = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name
