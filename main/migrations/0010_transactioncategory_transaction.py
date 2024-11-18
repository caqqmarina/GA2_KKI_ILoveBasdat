# Generated by Django 5.1.1 on 2024-11-18 14:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_user_mypay_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionCategory',
            fields=[
                ('category_id', models.IntegerField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.transactioncategory')),
            ],
        ),
    ]