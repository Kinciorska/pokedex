from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from .utils import TYPE_CHOICES


class Pokemon(models.Model):
    pokemon_id = models.IntegerField(unique=True)
    pokemon_name = models.CharField(max_length=100, unique=True)
    pokemon_height = models.IntegerField()
    pokemon_weight = models.IntegerField()
    pokemon_img = models.FilePathField(max_length=200, null=True)
    pokemon_img_shiny = models.FilePathField(max_length=200, null=True)
    pokemon_entry = models.TextField(max_length=1000, blank=True, default='')
    pokemon_type_1 = models.CharField(max_length=50, choices=TYPE_CHOICES)
    pokemon_type_2 = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, default='')

    class Meta:
        ordering = ['pokemon_id']


class FavouritePokemon(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Favourite Pokemons"

    def __str__(self):
        return self.pokemon.pokemon_name


class Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pokemon_id = models.ManyToManyField(Pokemon, related_name='pokemon')
    pokemon_number = models.IntegerField()

    class Meta:
        verbose_name_plural = "PokemonsInTeams"
        ordering = ['pokemon_number']
        constraints = [
            UniqueConstraint(
                fields=['user', 'pokemon_number'],
                name='unique_team',
                violation_error_message="There are already 6 pokemons in your team", )
        ]

    def __str__(self):
        return str(self.id)


class Move(models.Model):
    move_id = models.IntegerField(unique=True)
    move_name = models.CharField(max_length=100, unique=True)
    move_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    accuracy_validator = [MinValueValidator(0), MaxValueValidator(100)]
    move_accuracy = models.SmallIntegerField(validators=accuracy_validator, null=True)
    move_pp = models.SmallIntegerField(null=True)
    priority_validator = [MinValueValidator(-8), MaxValueValidator(8)]
    move_priority = models.SmallIntegerField(validators=priority_validator, null=True)
    move_power = models.SmallIntegerField(null=True)
    move_damage_class = models.CharField(max_length=100, null=True)
    move_entry = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.move_name


class PokemonInTeamQuerySet(models.QuerySet):
    def in_team(self, user):
        pokemon_pk_query = Team.objects.filter(user=user)
        pokemon_pk = list(pokemon_pk_query.values_list('pokemon_id', flat=True))
        return self.filter(pokemon_id__in=pokemon_pk)


class PokemonMoves(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    move_number = models.SmallIntegerField()
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    move = models.ForeignKey(Move, on_delete=models.CASCADE)

    objects = PokemonInTeamQuerySet.as_manager()

    class Meta:
        ordering = ['move_number']
        constraints = [
            UniqueConstraint(
                fields=['pokemon', 'move_number', 'user'],
                name='4_moves',
                violation_error_message="There are already 4 moves assigned to this pokemon", ),
        ]

    def __str__(self):
        return str(self.move)
