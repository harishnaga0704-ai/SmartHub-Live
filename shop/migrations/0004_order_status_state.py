from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0003_repair_order_customer_columns")]

    # ``status`` already exists in the legacy MySQL table.  This records it in
    # Django's migration state without trying to add the column a second time.
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="order",
                    name="status",
                    field=models.CharField(default="Completed", max_length=30),
                ),
            ],
        ),
    ]
