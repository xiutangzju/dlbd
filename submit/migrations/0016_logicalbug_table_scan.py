# Generated by Django 4.2.3 on 2023-08-14 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("submit", "0015_logicalbug_sqlfile"),
    ]

    operations = [
        migrations.AddField(
            model_name="logicalbug",
            name="table_scan",
            field=models.CharField(default="", max_length=1024),
        ),
    ]
