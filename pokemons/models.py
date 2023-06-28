from django.db import models
from django.db.models import CheckConstraint, Q
from django.core.exceptions import ValidationError


from django.contrib.auth.models import User


class FavouritePokemon(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "FavouritePokemons"

    def __str__(self):
        return self.name


class PokemonInTeam(models.Model):
    name = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField(unique=True)

    class Meta:
        verbose_name_plural = "PokemonsInTeams"
        constraints = [
            CheckConstraint(
                check=Q(number__lt=6),
                name='check_number_in_team',
                violation_error_message="There are already 6 pokemons in you team",
            ),
        ]

    def __str__(self):
        return self.name
