# Generated by Django 2.2.9 on 2020-02-12 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("organization", "0010_auto_20200212_1942")]

    operations = [
        migrations.AddField(
            model_name="location",
            name="image",
            field=models.ImageField(
                default="organization/product/default.png",
                upload_to="organization/product/",
            ),
        ),
        migrations.AddField(
            model_name="location", name="size", field=models.FloatField(default=0.0)
        ),
    ]