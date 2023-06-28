from django.db import models

from django.contrib.auth.models import User


class FavouritePokemon(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "FavouritePokemons"

    def __str__(self):
        return self.name
