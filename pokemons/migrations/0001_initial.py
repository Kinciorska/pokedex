# Generated by Django 4.2.1 on 2023-08-10 08:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pokemon_id', models.IntegerField(unique=True)),
                ('pokemon_name', models.CharField(max_length=200, unique=True)),
                ('pokemon_type_1', models.CharField(max_length=200)),
                ('pokemon_type_2', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pokemon_number', models.IntegerField(unique=True)),
                ('pokemon_id', models.ManyToManyField(to='pokemons.pokemon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'PokemonsInTeams',
                'ordering': ['pokemon_number'],
            },
        ),
        migrations.CreateModel(
            name='FavouritePokemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pokemon_id', models.IntegerField(unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'FavouritePokemons',
            },
        ),
        migrations.AddConstraint(
            model_name='team',
            constraint=models.CheckConstraint(check=models.Q(('pokemon_number__lt', 6)), name='check_number_in_team', violation_error_message='There are already 6 pokemons in you team'),
        ),
    ]
