# Generated by Bolt 5.0.dev20230915175420 on 2023-09-18 19:08

from bolt.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boltadmin", "0002_alter_dashboard_cards"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Dashboard",
        ),
    ]