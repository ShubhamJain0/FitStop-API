# Generated by Django 3.0 on 2021-03-14 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_storeitem_example2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ordereditem',
            field=models.ManyToManyField(null=True, to='api.Cart'),
        ),
    ]
