# Generated by Bolt 5.0.dev20240109202955 on 2024-01-09 21:36

from bolt.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("boltqueue", "0008_jobrequest_source_jobresult_source"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobresult",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("", "Unknown"),
                    ("PROCESSING", "Processing"),
                    ("SUCCESSFUL", "Successful"),
                    ("ERRORED", "Errored"),
                    ("TIMED_OUT", "Timed out"),
                ],
                db_index=True,
                default="",
                max_length=20,
            ),
        ),
    ]
