# Generated by Django 2.2.9 on 2020-02-24 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("user", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="show_information_tooltips",
            field=models.BooleanField(default=True),
        )
    ]
