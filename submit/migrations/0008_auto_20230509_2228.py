# Generated by Django 3.2.17 on 2023-05-09 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0007_remove_logicalbug_execution_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='logicalbug',
            name='minimal_execution_plan',
            field=models.CharField(default='', max_length=1023),
        ),
        migrations.AddField(
            model_name='logicalbug',
            name='original_execution_plan',
            field=models.CharField(default='', max_length=1023),
        ),
    ]
