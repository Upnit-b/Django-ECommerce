# Generated by Django 5.2 on 2025-05-05 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("carts", "0004_alter_cartitem_variations"),
        ("store", "0005_reviewrating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cartitem",
            name="variations",
            field=models.ManyToManyField(to="store.variation"),
        ),
    ]
