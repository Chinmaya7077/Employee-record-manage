# Generated by Django 5.1.4 on 2025-01-28 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskapp', '0008_alter_task_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='mail_id',
            field=models.EmailField(max_length=100, unique=True),
        ),
    ]
