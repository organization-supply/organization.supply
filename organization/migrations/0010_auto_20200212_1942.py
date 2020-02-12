# Generated by Django 2.2.9 on 2020-02-12 19:42

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0003_taggeditem_add_unique_index"),
        ("organization", "0009_auto_20200212_1835"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="organization.OrganizationTaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="organization.OrganizationTaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
