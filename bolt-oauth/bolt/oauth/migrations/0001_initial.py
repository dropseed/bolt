# Generated by Bolt 4.0.3 on 2022-03-16 19:11

import bolt.db.models.deletion
from bolt.runtime import settings
from bolt.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OAuthConnection",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("provider_key", models.CharField(db_index=True, max_length=100)),
                ("provider_user_id", models.CharField(db_index=True, max_length=100)),
                ("access_token", models.CharField(blank=True, max_length=100)),
                ("refresh_token", models.CharField(blank=True, max_length=100)),
                (
                    "access_token_expires_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "refresh_token_expires_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=bolt.db.models.deletion.CASCADE,
                        related_name="oauth_connections",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("provider_key",),
                "unique_together": {("provider_key", "provider_user_id")},
            },
        ),
    ]
