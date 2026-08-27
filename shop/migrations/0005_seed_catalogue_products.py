from django.db import migrations


CATALOGUE_PRODUCTS = [
    # name, category, MRP, offer price, rating
    ("iPhone 16", "Mobile", 99999, 74999, 5), ("Samsung S25 Ultra", "Mobile", 129999, 109999, 5),
    ("Google Pixel 9 Pro", "Mobile", 99999, 84999, 4), ("OnePlus 13", "Mobile", 84999, 59999, 5),
    ("Xiaomi 15", "Mobile", 64999, 54999, 4), ("Vivo X200 Pro", "Mobile", 99999, 79999, 5),
    ("Oppo Find X8 Pro", "Mobile", 94999, 74999, 5), ("Realme GT 7 Pro", "Mobile", 55999, 44999, 4),
    ("Nothing Phone 3", "Mobile", 69999, 49999, 5), ("Motorola Edge 60 Pro", "Mobile", 54999, 39999, 4),
    ("iQOO 13", "Mobile", 66999, 54999, 5), ("Redmi Note 14 Pro+", "Mobile", 49999, 29999, 4),
    ("MacBook Air M4", "Laptop", 119999, 94999, 5), ("Dell XPS 14", "Laptop", 159999, 124999, 5),
    ("HP Spectre x360", "Laptop", 149999, 109999, 5), ("Lenovo Legion Pro 7", "Laptop", 219999, 179999, 5),
    ("ASUS ROG Zephyrus G16", "Laptop", 209999, 164999, 5), ("Acer Predator Neo 16", "Laptop", 134999, 114999, 4),
    ("MSI Raider GE78", "Laptop", 259999, 209999, 5), ("Galaxy Book5 Pro", "Laptop", 132999, 109999, 4),
    ("HP Victus 15", "Laptop", 99999, 69999, 4), ("ASUS Vivobook S15", "Laptop", 104999, 74999, 4),
    ("Lenovo IdeaPad Slim 5", "Laptop", 79999, 59999, 4), ("Dell Inspiron 15", "Laptop", 80999, 54999, 4),
    ("Sony WH-1000XM5", "Headphones", 35999, 24999, 5), ("Apple AirPods Max", "Headphones", 66999, 49999, 5),
    ("Bose QC Ultra", "Headphones", 37999, 29999, 5), ("JBL Tour One M2", "Headphones", 28999, 18999, 4),
    ("Sennheiser Momentum 4", "Headphones", 34999, 26999, 5), ("Beats Studio Pro", "Headphones", 33999, 23999, 4),
    ("boAt Nirvana 751 ANC", "Headphones", 6999, 3999, 4), ("Skullcandy Crusher Evo", "Headphones", 18999, 11999, 5),
    ("Soundcore Q45", "Headphones", 14499, 11499, 4), ("Logitech G733", "Headphones", 15999, 10999, 5),
    ("Razer BlackShark V2 Pro", "Headphones", 19999, 15999, 5), ("Sony INZONE H9", "Headphones", 24999, 17999, 5),
    ("Apple Watch Series 10", "Smart Watch", 59999, 44999, 5), ("Samsung Galaxy Watch Ultra", "Smart Watch", 69999, 49999, 5),
    ("Garmin Venu 3", "Smart Watch", 49999, 39999, 5), ("Amazfit Balance", "Smart Watch", 24999, 18999, 4),
    ("OnePlus Watch 2", "Smart Watch", 29999, 22999, 5), ("Noise ColorFit Pro 6", "Smart Watch", 7499, 4499, 4),
    ("boAt Lunar Pro LTE", "Smart Watch", 9999, 5999, 4), ("Fire-Boltt Dream", "Smart Watch", 11999, 8999, 4),
    ("Fitbit Versa 4", "Smart Watch", 25999, 17999, 5), ("Huawei Watch GT 5", "Smart Watch", 30999, 21999, 5),
    ("CMF Watch Pro 2", "Smart Watch", 7499, 4999, 4), ("Xiaomi Watch S4", "Smart Watch", 21999, 14999, 5),
]


def seed_catalogue_products(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    for name, category, price, offer_price, rating in CATALOGUE_PRODUCTS:
        Product.objects.get_or_create(
            name=name,
            defaults={
                "category": category,
                "brand": name.split()[0],
                "price": price,
                "offer_price": offer_price,
                "stock": 10,
                "rating": rating,
            },
        )


def remove_seeded_catalogue_products(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    Product.objects.filter(name__in=[product[0] for product in CATALOGUE_PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [("shop", "0004_order_status_state")]

    operations = [migrations.RunPython(seed_catalogue_products, remove_seeded_catalogue_products)]
