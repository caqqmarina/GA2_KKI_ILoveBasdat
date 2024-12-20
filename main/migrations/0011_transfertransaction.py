# Generated by Django 5.1.1 on 2024-11-18 15:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_transactioncategory_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferTransaction',
            fields=[
                ('transaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.transaction')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
            bases=('main.transaction',),
        ),
    ]
