# Generated by Django 5.0.8 on 2024-11-17 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_merge_20241117_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerprofile',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]