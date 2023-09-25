from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.core.exceptions import ValidationError


from django.contrib.auth.models import User


class Pokemon(models.Model):
    pokemon_id = models.IntegerField(unique=True)
    pokemon_name = models.CharField(max_length=200, unique=True)
    pokemon_type_1 = models.CharField(max_length=200)
    pokemon_type_2 = models.CharField(max_length=200, blank=True, default='')


class FavouritePokemon(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Favourite Pokemons"

    def __str__(self):
        return self.pokemon.pokemon_name


# class PokemonInTeam(models.Model):
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     pokemon = models.ManyToManyField(Pokemon)
#     order = models.PositiveSmallIntegerField()
#
# class Team:
#     name = models.CharField(max_length=50)
#     user = models.OneToOneField(to=User)


class Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pokemon_id = models.ManyToManyField(Pokemon)
    pokemon_number = models.IntegerField()

    class Meta:
        verbose_name_plural = "PokemonsInTeams"
        ordering = ['pokemon_number']
        constraints = [
            UniqueConstraint(
                fields=['user', 'pokemon_number'],
                name='unique_team',
                violation_error_message= "There are already 6 pokemons in your team",)
                ]

    def __str__(self):
        return str(self.id)


# class Move(models.Model):
#     move_name = models.CharField(max_length=200)
#     move_type = models.CharField(max_length=200)
#     move_number = models.IntegerField(unique=True)
#     pokemon = models.ManyToManyField(Pokemon)
#
#
#
#     class Meta:
#         verbose_name_plural = "Pokemons"
#         constraints = [
#             CheckConstraint(
#                 check=Q(move_number__lt=4),
#                 name='check_moves_number',
#                 violation_error_message="You already chose 4 moves for this pokemon",
#             ),
#         ]
#
#     def __str__(self):
#         return self.name

