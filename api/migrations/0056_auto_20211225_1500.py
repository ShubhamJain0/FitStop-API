# Generated by Django 3.0 on 2021-12-25 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0055_auto_20211209_1352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detailsimage',
            name='item',
        ),
        migrations.DeleteModel(
            name='HomeProducts',
        ),
        migrations.DeleteModel(
            name='DetailsImage',
        ),
    ]
