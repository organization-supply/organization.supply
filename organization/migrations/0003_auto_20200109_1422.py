# Generated by Django 2.2 on 2020-01-09 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("organization", "0002_notification")]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="organization",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="organization.Organization",
            ),
        )
    ]
