# Generated by Django 5.0.8 on 2024-11-17 21:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_promo_voucher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workerprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
        migrations.DeleteModel(
            name='WorkerProfile',
        ),
    ]