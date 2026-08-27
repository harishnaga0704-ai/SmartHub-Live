# Repairs the legacy ``shop_order`` table used by the existing MySQL database.
# The earlier migration history is marked as applied, but this table only has
# id, product_id, quantity, status and created_at columns.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_alter_order_id_alter_product_id"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE shop_order
                    ADD COLUMN customer_name varchar(100) NOT NULL DEFAULT 'Walk-in Customer',
                    ADD COLUMN email varchar(254) NOT NULL DEFAULT '',
                    ADD COLUMN phone varchar(20) NOT NULL DEFAULT '',
                    ADD COLUMN address longtext NULL,
                    ADD COLUMN total decimal(10,2) NOT NULL DEFAULT 0.00,
                    ADD COLUMN created datetime(6) NULL
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
                UPDATE shop_order
                SET address = COALESCE(address, ''),
                    created = COALESCE(created, created_at, UTC_TIMESTAMP(6))
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
                ALTER TABLE shop_order
                    MODIFY COLUMN address longtext NOT NULL,
                    MODIFY COLUMN created datetime(6) NOT NULL
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
