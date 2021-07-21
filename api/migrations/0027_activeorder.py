# Generated by Django 3.0 on 2021-05-01 06:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20210427_1530'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_status', models.CharField(choices=[('Order Placed', 'Order Placed'), ('Order Confirmed', 'Order Confirmed'), ('Out for delivery', 'Out for delivery'), ('Order Cancelled', 'Order Cancelled')], default='Order Placed', max_length=255)),
                ('push_token', models.CharField(max_length=255, null=True)),
                ('order_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]