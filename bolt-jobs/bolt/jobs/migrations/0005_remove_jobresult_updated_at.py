# Generated by Bolt 5.0.dev20231228223551 on 2023-12-28 22:57

from bolt.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boltqueue", "0004_alter_jobresult_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="jobresult",
            name="updated_at",
        ),
    ]
