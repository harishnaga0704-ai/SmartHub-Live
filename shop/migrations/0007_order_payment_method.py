from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0006_order_is_seen"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(default="COD", max_length=20),
        ),
    ]
