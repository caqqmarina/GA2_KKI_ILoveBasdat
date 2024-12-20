from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_booking_status_testimonial_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_name', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('waiting_for_departure', 'Waiting for Worker to Depart'), ('arrived_at_location', 'Worker Arrived at Location'), ('service_in_progress', 'Service in Progress'), ('order_completed', 'Order Completed'), ('order_canceled', 'Order Canceled')], default='waiting_for_departure', max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
