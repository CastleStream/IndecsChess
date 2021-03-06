# Generated by Django 3.0.3 on 2020-10-21 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chessapp', '0005_auto_20201021_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='currentELO',
            field=models.FloatField(default=1200),
        ),
        migrations.AlterField(
            model_name='profile',
            name='highestELO',
            field=models.FloatField(default=1200),
        ),
        migrations.AlterField(
            model_name='profile',
            name='lowestELO',
            field=models.FloatField(default=1200),
        ),
    ]
