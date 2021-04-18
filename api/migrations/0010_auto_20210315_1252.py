# Generated by Django 3.0 on 2021-03-15 12:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20210315_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='customusermodel',
            name='selected_option',
            field=models.CharField(choices=[('one', 'one'), ('two', 'two'), ('three', 'three'), ('four', 'four')], max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customusermodel',
            name='phone',
            field=models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator('^\\d{10}$')]),
        ),
    ]