# Generated by Django 5.0.8 on 2024-11-18 15:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_remove_workerprofile_user_delete_userprofile_and_more'),
        ('services', '0005_workerserviceorder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workerserviceorder',
            name='worker',
        ),
        migrations.AddField(
            model_name='workerserviceorder',
            name='assigned_worker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to='main.worker'),
        ),
        migrations.AddField(
            model_name='workerserviceorder',
            name='workers',
            field=models.ManyToManyField(related_name='available_orders', to='main.worker'),
        ),
    ]
