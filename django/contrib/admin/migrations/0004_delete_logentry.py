# Generated by Django 5.0.dev20230529221603 on 2023-05-30 01:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("admin", "0003_logentry_add_action_flag_choices"),
    ]

    operations = [
        migrations.DeleteModel(
            name="LogEntry",
        ),
    ]