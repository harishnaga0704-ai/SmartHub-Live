from django.db import migrations, models


def add_created_at_if_missing(apps, schema_editor):
    Order = apps.get_model("shop", "Order")
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        columns = {
            column.name
            for column in connection.introspection.get_table_description(cursor, Order._meta.db_table)
        }
    if "created_at" in columns:
        return

    nullable_field = models.DateTimeField(null=True)
    nullable_field.set_attributes_from_name("created_at")
    schema_editor.add_field(Order, nullable_field)
    table_name = schema_editor.quote_name(Order._meta.db_table)
    schema_editor.execute(
        f"UPDATE {table_name} SET created_at = created WHERE created_at IS NULL"
    )
    field = models.DateTimeField(auto_now_add=True)
    field.set_attributes_from_name("created_at")
    schema_editor.alter_field(Order, nullable_field, field, strict=False)


def reverse_add_created_at_if_missing(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    """Register an existing legacy MySQL column with Django's model state."""

    dependencies = [
        ("shop", "0008_order_customer"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_created_at_if_missing, reverse_add_created_at_if_missing),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="order",
                    name="created_at",
                    field=models.DateTimeField(auto_now_add=True),
                ),
            ],
        ),
    ]
