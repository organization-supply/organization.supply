# Generated by Django 2.2.9 on 2020-02-04 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("organization", "0007_auto_20200118_1419")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(
                default="organization/product/default.png",
                upload_to="organization/product/",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="price_cost",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="product",
            name="price_sale",
            field=models.FloatField(default=0.0),
        ),
    ]
