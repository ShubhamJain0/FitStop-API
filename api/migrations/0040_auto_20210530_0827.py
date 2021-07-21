# Generated by Django 3.0 on 2021-05-30 08:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_auto_20210529_1423'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='previousorder',
            name='ordereditems',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('weight', models.CharField(max_length=255, null=True)),
                ('price', models.IntegerField()),
                ('count', models.IntegerField(default=1)),
                ('id_of_recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='PreviousOrderItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=255, null=True)),
                ('item_weight', models.CharField(max_length=255, null=True)),
                ('item_price', models.IntegerField()),
                ('item_count', models.IntegerField()),
                ('id_of_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.PreviousOrder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]