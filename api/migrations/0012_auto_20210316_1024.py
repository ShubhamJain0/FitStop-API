# Generated by Django 3.0 on 2021-03-16 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20210316_1004'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Banner',
            new_name='HomeBanner',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to='images/recipe/'),
        ),
    ]