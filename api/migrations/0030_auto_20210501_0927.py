# Generated by Django 3.0 on 2021-05-01 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20210501_0743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activeorder',
            name='push_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
