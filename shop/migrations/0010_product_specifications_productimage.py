from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("shop", "0009_order_created_at_state")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="specifications",
            field=models.TextField(blank=True, help_text="Enter one specification per line, for example: Display: 6.7 inch"),
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("view_name", models.CharField(choices=[("Front", "Front View"), ("Back", "Back View"), ("Side", "Side View"), ("Size", "Size / Dimensions"), ("Other", "Other View")], default="Other", max_length=20)),
                ("image", models.ImageField(upload_to="products/details/")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="detail_images", to="shop.product")),
            ],
            options={"ordering": ("id",)},
        ),
    ]
