# Generated by Plain 4.0.6 on 2022-08-11 19:18

from plain import models
from plain.models import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("plainoauth", "0002_alter_oauthconnection_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="oauthconnection",
            name="access_token",
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name="oauthconnection",
            name="refresh_token",
            field=models.CharField(blank=True, max_length=300),
        ),
    ]