# Generated by Django 3.0 on 2021-06-01 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_auto_20210531_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='NutritionalValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('value', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
