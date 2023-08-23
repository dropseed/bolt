# Generated by Bolt 4.1.7 on 2023-03-21 19:54

import uuid

import bolt.db.models.deletion
import bolt.flags.models
from bolt.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Flag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        validators=[bolt.flags.models.validate_flag_name],
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("enabled", models.BooleanField(default=True)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="FlagResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("key", models.CharField(max_length=255)),
                ("value", models.JSONField()),
                (
                    "flag",
                    models.ForeignKey(
                        on_delete=bolt.db.models.deletion.CASCADE,
                        to="boltflags.flag",
                    ),
                ),
            ],
            options={
                "unique_together": {("flag", "key")},
            },
        ),
    ]
