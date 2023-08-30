# Generated by Django 3.2.17 on 2023-05-08 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('submit', '0002_alter_testfile_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogicalBug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bug_id', models.IntegerField()),
                ('severity', models.IntegerField()),
                ('database', models.CharField(max_length=63)),
                ('category', models.CharField(max_length=63)),
                ('operator', models.CharField(max_length=63)),
                ('status', models.BooleanField(default=False)),
                ('original_query', models.CharField(max_length=1023)),
                ('minimal_query', models.CharField(max_length=511)),
                ('execution_plan', models.CharField(max_length=1023)),
                ('original_ground_truth', models.CharField(max_length=1023)),
                ('original_query_result', models.CharField(max_length=1023)),
                ('minimal_ground_truth', models.CharField(max_length=1023)),
                ('minimal_query_result', models.CharField(max_length=1023)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='submit.user')),
            ],
        ),
    ]
