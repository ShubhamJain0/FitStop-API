# Generated by Django 3.0 on 2021-05-27 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0034_auto_20210517_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='item',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
