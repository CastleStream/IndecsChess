# Generated by Django 3.0.3 on 2020-10-20 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chessapp', '0003_game'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='player1Elo',
            new_name='player1ELO',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='player2Elo',
            new_name='player2ELO',
        ),
        migrations.AlterField(
            model_name='profile',
            name='currentELO',
            field=models.IntegerField(default=1200),
        ),
        migrations.AlterField(
            model_name='profile',
            name='highestELO',
            field=models.IntegerField(default=1200),
        ),
        migrations.AlterField(
            model_name='profile',
            name='lowestELO',
            field=models.IntegerField(default=1200),
        ),
    ]