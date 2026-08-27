from django.db import migrations


def seed_products(apps, schema_editor):
    Product = apps.get_model('YOUR_APP_NAME', 'Product')

    products = [
        {"name": "iPhone 16", "category": "mobile", "brand": "Apple",
         "price": 79999, "offer_price": None, "stock": 25, "rating": 4.7},

        {"name": "MacBook Pro", "category": "laptop", "brand": "Apple",
         "price": 89999, "offer_price": None, "stock": 12, "rating": 4.8},

        {"name": "Apple AirPods", "category": "headphone", "brand": "Apple",
         "price": 8999, "offer_price": None, "stock": 40, "rating": 4.5},

        {"name": "Apple Watch Series", "category": "smartwatch", "brand": "Apple",
         "price": 10999, "offer_price": None, "stock": 30, "rating": 4.6},

        {"name": "Samsung S23 Ultra", "category": "mobile", "brand": "Samsung",
         "price": 54999, "offer_price": None, "stock": 20, "rating": 4.6},

        {"name": "Samsung Airpodes", "category": "headphone", "brand": "Samsung",
         "price": 16999, "offer_price": None, "stock": 35, "rating": 4.2},

        {"name": "Samsung Airbook Series", "category": "laptop", "brand": "Samsung",
         "price": 49999, "offer_price": None, "stock": 15, "rating": 4.3},

        {"name": "Vivo X300", "category": "mobile", "brand": "Vivo",
         "price": 4999, "offer_price": None, "stock": 50, "rating": 4.0},

        {"name": "Nothing 3a", "category": "mobile", "brand": "Nothing",
         "price": 24999, "offer_price": None, "stock": 28, "rating": 4.4},

        {"name": "Google Pixel 10a", "category": "mobile", "brand": "Google",
         "price": 49999, "offer_price": None, "stock": 22, "rating": 4.5},

        {"name": "Oppo Find X9", "category": "mobile", "brand": "Oppo",
         "price": 34999, "offer_price": None, "stock": 18, "rating": 4.3},

        {"name": "Xiaomi 17 Promax", "category": "mobile", "brand": "Xiaomi",
         "price": 114999, "offer_price": None, "stock": 10, "rating": 4.7},
    ]

    for p in products:
        Product.objects.get_or_create(
            name=p["name"],
            defaults={
                "category": p["category"],
                "brand": p["brand"],
                "price": p["price"],
                "offer_price": p["offer_price"],
                "stock": p["stock"],
                "rating": p["rating"],
            }
        )


def remove_products(apps, schema_editor):
    Product = apps.get_model('YOUR_APP_NAME', 'Product')
    names = [
        "iPhone 16", "MacBook Pro", "Apple AirPods", "Apple Watch Series",
        "Samsung S23 Ultra", "Samsung Airpodes", "Samsung Airbook Series",
        "Vivo X300", "Nothing 3a", "Google Pixel 10a", "Oppo Find X9",
        "Xiaomi 17 Promax",
    ]
    Product.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    # IMPORTANT: change this to your app's last migration file name,
    # e.g. ('YOUR_APP_NAME', '0001_initial')
    dependencies = [
        ('YOUR_APP_NAME', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_products, remove_products),
    ]
