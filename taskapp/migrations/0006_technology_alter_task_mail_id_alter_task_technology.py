# Generated by Django 5.1.4 on 2025-01-20 11:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskapp', '0005_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Technology',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='task',
            name='mail_id',
            field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name='task',
            name='technology',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='taskapp.technology'),
        ),
    ]
