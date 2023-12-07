from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth.models import User

from pokemons.models import Pokemon
from pokemons.queryset import PokemonInTeamQuerySet


class Move(models.Model):
    move_id = models.IntegerField(unique=True)
    move_name = models.CharField(max_length=200, unique=True)
    move_type = models.CharField(max_length=200)

    def __str__(self):
        return self.move_name


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
