# Repairs the legacy ``shop_order`` table without duplicating columns on a
# fresh database created from the complete migration history.

from django.db import migrations, models


def repair_order_columns(apps, schema_editor):
    Order = apps.get_model("shop", "Order")
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        existing_columns = {
            column.name
            for column in connection.introspection.get_table_description(cursor, Order._meta.db_table)
        }

    defaults = {
        "customer_name": "Walk-in Customer",
        "email": "",
        "phone": "",
        "address": "",
        "total": 0,
    }
    for field_name, default in defaults.items():
        if field_name in existing_columns:
            continue
        field = Order._meta.get_field(field_name).clone()
        field.default = default
        schema_editor.add_field(Order, field)

    if "created" not in existing_columns:
        field = Order._meta.get_field("created").clone()
        field.null = True
        schema_editor.add_field(Order, field)
        Order.objects.filter(created__isnull=True).update(created=models.F("created_at"))
        field.null = False
        schema_editor.alter_field(Order, field, Order._meta.get_field("created"), strict=False)


def reverse_repair_order_columns(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_alter_order_id_alter_product_id"),
    ]

    operations = [
        migrations.RunPython(repair_order_columns, reverse_repair_order_columns),
    ]
