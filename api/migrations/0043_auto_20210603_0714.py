# Generated by Django 3.0 on 2021-06-03 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_nutritionalvalue'),
    ]

    operations = [
        migrations.RenameField(
            model_name='previousorder',
            old_name='price',
            new_name='total_price',
        ),
        migrations.AddField(
            model_name='order',
            name='cart_total',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_charges',
            field=models.IntegerField(default=25),
        ),
        migrations.AddField(
            model_name='order',
            name='taxes',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='previousorder',
            name='cart_total',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='previousorder',
            name='coupon',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='previousorder',
            name='delivery_charges',
            field=models.IntegerField(default=25),
        ),
        migrations.AddField(
            model_name='previousorder',
            name='taxes',
            field=models.IntegerField(default=30),
        ),
    ]
