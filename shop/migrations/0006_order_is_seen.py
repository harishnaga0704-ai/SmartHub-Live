from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0005_seed_catalogue_products")]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_seen",
            field=models.BooleanField(default=False),
        ),
    ]
