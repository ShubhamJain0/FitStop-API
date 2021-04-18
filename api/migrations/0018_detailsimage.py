# Generated by Django 3.0 on 2021-04-16 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_auto_20210405_0819'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetailsImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to='images/detailsimage/')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.StoreItem')),
            ],
        ),
    ]