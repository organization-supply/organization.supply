# Generated by Django 2.2 on 2020-01-09 13:24

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organization", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("success", "success"),
                            ("info", "info"),
                            ("warning", "warning"),
                            ("error", "error"),
                        ],
                        default="info",
                        max_length=20,
                    ),
                ),
                ("verb", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("unread", models.BooleanField(db_index=True, default=True)),
                ("actor_object_id", models.CharField(max_length=255)),
                (
                    "target_object_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "action_object_object_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                ("public", models.BooleanField(db_index=True, default=True)),
                ("deleted", models.BooleanField(db_index=True, default=False)),
                ("emailed", models.BooleanField(db_index=True, default=False)),
                (
                    "action_object_content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notify_action_object",
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "actor_content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notify_actor",
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organization.Organization",
                    ),
                ),
                (
                    "target_content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notify_target",
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-timestamp",),
                "index_together": {("user", "unread")},
            },
        )
    ]
