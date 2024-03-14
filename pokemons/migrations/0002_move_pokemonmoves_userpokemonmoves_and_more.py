# Generated by Django 4.2.4 on 2024-03-13 12:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pokemons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('move_id', models.IntegerField(unique=True)),
                ('move_name', models.CharField(max_length=100, unique=True)),
                ('move_type', models.CharField(choices=[('grass', 'GRASS'), ('fire', 'FIRE'), ('water', 'WATER'), ('bug', 'BUG'), ('normal', 'NORMAL'), ('poison', 'POISON'), ('electric', 'ELECTRIC'), ('ground', 'GROUND'), ('fighting', 'FIGHTING'), ('psychic', 'PSYCHIC'), ('rock', 'ROCK'), ('ghost', 'GHOST'), ('ice', 'ICE'), ('dragon', 'DRAGON'), ('dark', 'DARK'), ('steel', 'STEEL'), ('flying', 'FLYING'), ('', None)], max_length=50)),
                ('move_accuracy', models.SmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('move_pp', models.SmallIntegerField(null=True)),
                ('move_priority', models.SmallIntegerField(null=True, validators=[django.core.validators.MinValueValidator(-8), django.core.validators.MaxValueValidator(8)])),
                ('move_power', models.SmallIntegerField(null=True)),
                ('move_damage_class', models.CharField(max_length=100, null=True)),
                ('move_entry', models.TextField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PokemonMoves',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='UserPokemonMoves',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('move_number', models.SmallIntegerField()),
            ],
            options={
                'ordering': ['move_number'],
            },
        ),
        migrations.AlterModelOptions(
            name='favouritepokemon',
            options={'verbose_name_plural': 'Favourite Pokemons'},
        ),
        migrations.AlterModelOptions(
            name='pokemon',
            options={'ordering': ['pokemon_id']},
        ),
        migrations.RemoveConstraint(
            model_name='team',
            name='check_number_in_team',
        ),
        migrations.RemoveField(
            model_name='favouritepokemon',
            name='pokemon_id',
        ),
        migrations.RemoveField(
            model_name='team',
            name='pokemon_id',
        ),
        migrations.AddField(
            model_name='favouritepokemon',
            name='pokemon',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pokemons.pokemon'),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_entry',
            field=models.TextField(blank=True, default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_height',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_img',
            field=models.FilePathField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_img_shiny',
            field=models.FilePathField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='pokemon',
            name='pokemon_weight',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='team',
            name='pokemon',
            field=models.ManyToManyField(related_name='pokemon_in_team', to='pokemons.pokemon'),
        ),
        migrations.AlterField(
            model_name='favouritepokemon',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='pokemon',
            name='pokemon_name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='pokemon',
            name='pokemon_type_1',
            field=models.CharField(choices=[('grass', 'GRASS'), ('fire', 'FIRE'), ('water', 'WATER'), ('bug', 'BUG'), ('normal', 'NORMAL'), ('poison', 'POISON'), ('electric', 'ELECTRIC'), ('ground', 'GROUND'), ('fighting', 'FIGHTING'), ('psychic', 'PSYCHIC'), ('rock', 'ROCK'), ('ghost', 'GHOST'), ('ice', 'ICE'), ('dragon', 'DRAGON'), ('dark', 'DARK'), ('steel', 'STEEL'), ('flying', 'FLYING'), ('', None)], max_length=50),
        ),
        migrations.AlterField(
            model_name='pokemon',
            name='pokemon_type_2',
            field=models.CharField(blank=True, choices=[('grass', 'GRASS'), ('fire', 'FIRE'), ('water', 'WATER'), ('bug', 'BUG'), ('normal', 'NORMAL'), ('poison', 'POISON'), ('electric', 'ELECTRIC'), ('ground', 'GROUND'), ('fighting', 'FIGHTING'), ('psychic', 'PSYCHIC'), ('rock', 'ROCK'), ('ghost', 'GHOST'), ('ice', 'ICE'), ('dragon', 'DRAGON'), ('dark', 'DARK'), ('steel', 'STEEL'), ('flying', 'FLYING'), ('', None)], default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='team',
            name='pokemon_number',
            field=models.IntegerField(),
        ),
        migrations.AddConstraint(
            model_name='team',
            constraint=models.UniqueConstraint(fields=('user', 'pokemon_number'), name='unique_team', violation_error_message='There are already 6 pokemons in your team'),
        ),
        migrations.AddField(
            model_name='userpokemonmoves',
            name='move',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemons.move'),
        ),
        migrations.AddField(
            model_name='userpokemonmoves',
            name='pokemon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemons.pokemon'),
        ),
        migrations.AddField(
            model_name='userpokemonmoves',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pokemonmoves',
            name='move',
            field=models.ManyToManyField(related_name='move', to='pokemons.move'),
        ),
        migrations.AddField(
            model_name='pokemonmoves',
            name='pokemon',
            field=models.ManyToManyField(related_name='pokemon', to='pokemons.pokemon'),
        ),
        migrations.AddConstraint(
            model_name='userpokemonmoves',
            constraint=models.UniqueConstraint(fields=('pokemon', 'move_number', 'user'), name='4_moves', violation_error_message='There are already 4 moves assigned to this pokemon'),
        ),
    ]
