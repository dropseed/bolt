# Generated by Bolt 5.0.dev20231223023818 on 2023-12-23 03:30

import uuid

from bolt.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobRequest",
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
                ("job_class", models.CharField(db_index=True, max_length=255)),
                ("parameters", models.JSONField(blank=True, null=True)),
                ("priority", models.IntegerField(db_index=True, default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "started_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                (
                    "completed_at",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("error", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["priority", "-created_at"],
            },
        ),
    ]