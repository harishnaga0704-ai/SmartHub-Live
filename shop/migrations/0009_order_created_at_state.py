from django.db import migrations, models


class Migration(migrations.Migration):
    """Register an existing legacy MySQL column with Django's model state."""

    dependencies = [
        ("shop", "0008_order_customer"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="order",
                    name="created_at",
                    field=models.DateTimeField(auto_now_add=True),
                ),
            ],
        ),
    ]
