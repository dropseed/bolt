# Generated by Plain 4.0.3 on 2022-03-18 18:24

from plain import models
from plain.models import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("plainoauth", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="oauthconnection",
            options={
                "ordering": ("provider_key",),
            },
        ),
        migrations.AlterField(
            model_name="oauthconnection",
            name="access_token",
            field=models.CharField(max_length=100),
        ),
    ]
