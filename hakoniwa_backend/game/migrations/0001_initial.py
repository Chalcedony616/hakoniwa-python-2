# Generated by Django 5.0.7 on 2024-09-08 13:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn_count', models.IntegerField(default=0)),
                ('game_name', models.CharField(default='箱庭諸島２ for Python', max_length=100)),
                ('last_updated', models.DateTimeField()),
                ('is_updating', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.IntegerField()),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command', models.IntegerField()),
                ('coordinates', models.CharField(max_length=5)),
                ('target_island_id', models.IntegerField()),
                ('quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Island',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('owner', models.CharField(max_length=100)),
                ('comment', models.CharField(default='（未登録）', max_length=100)),
                ('discovery_turn', models.IntegerField()),
                ('population', models.IntegerField()),
                ('area', models.IntegerField()),
                ('funds', models.IntegerField()),
                ('food', models.IntegerField()),
                ('farm_size', models.IntegerField()),
                ('factory_size', models.IntegerField()),
                ('mine_size', models.IntegerField()),
                ('missile_capacity', models.IntegerField()),
                ('absent', models.IntegerField(default=178)),
                ('preparing', models.IntegerField(default=0)),
                ('propaganda', models.BooleanField(default=False)),
                ('monstersend', models.IntegerField(default=0)),
                ('monumentfly', models.IntegerField(default=0)),
                ('boatpeople', models.IntegerField(default=0)),
                ('turnprize', models.BooleanField(default=0)),
                ('prosperity', models.BooleanField(default=False)),
                ('superprosperity', models.BooleanField(default=False)),
                ('ultraprosperity', models.BooleanField(default=False)),
                ('peace', models.BooleanField(default=False)),
                ('superpeace', models.BooleanField(default=False)),
                ('ultrapeace', models.BooleanField(default=False)),
                ('tragedy', models.BooleanField(default=False)),
                ('supertragedy', models.BooleanField(default=False)),
                ('ultratragedy', models.BooleanField(default=False)),
                ('ranking', models.IntegerField(default=99)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IslandBackup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_island_id', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('owner', models.CharField(max_length=100)),
                ('discovery_turn', models.IntegerField()),
                ('population', models.IntegerField()),
                ('area', models.IntegerField()),
                ('funds', models.IntegerField()),
                ('food', models.IntegerField()),
                ('farm_size', models.IntegerField()),
                ('factory_size', models.IntegerField()),
                ('mine_size', models.IntegerField()),
                ('missile_capacity', models.IntegerField()),
                ('turnprize', models.BooleanField(default=0)),
                ('prosperity', models.BooleanField(default=False)),
                ('superprosperity', models.BooleanField(default=False)),
                ('ultraprosperity', models.BooleanField(default=False)),
                ('peace', models.BooleanField(default=False)),
                ('superpeace', models.BooleanField(default=False)),
                ('ultrapeace', models.BooleanField(default=False)),
                ('tragedy', models.BooleanField(default=False)),
                ('supertragedy', models.BooleanField(default=False)),
                ('ultratragedy', models.BooleanField(default=False)),
                ('map_data', models.JSONField()),
                ('backup_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('turn', models.IntegerField()),
                ('message', models.TextField()),
                ('is_confidential', models.BooleanField(default=False)),
                ('is_allLog', models.BooleanField(default=True)),
                ('island', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs', to='game.island')),
            ],
        ),
        migrations.CreateModel(
            name='MapTile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('terrain', models.IntegerField()),
                ('landvalue', models.IntegerField()),
                ('island', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='map_tiles', to='game.island')),
            ],
        ),
        migrations.AddField(
            model_name='island',
            name='map_data',
            field=models.ManyToManyField(related_name='island_maps', to='game.maptile'),
        ),
        migrations.AddField(
            model_name='island',
            name='plans',
            field=models.ManyToManyField(to='game.plan'),
        ),
    ]
