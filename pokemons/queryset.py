from django.db import models
from django.db.models import Q

from .models import Team


class PokemonInTeamQuerySet(models.QuerySet):
    def in_team(self, user):
        all_pokemons = (Team.objects.filter(user=user))
        pokemon_pk_list = list(all_pokemons.values_list('pokemon_id', flat=True))
        pokemons_number = len(pokemon_pk_list)
        match pokemons_number:
            case 0:
                return self.none()
            case 1:
                pk_1 = pokemon_pk_list[0]
                return self.filter(Q(pokemon=pk_1))
            case 2:
                pk_1 = pokemon_pk_list[0]
                pk_2 = pokemon_pk_list[1]
                return self.filter(Q(pokemon=pk_1) |
                                   Q(pokemon=pk_2))
            case 3:
                pk_1 = pokemon_pk_list[0]
                pk_2 = pokemon_pk_list[1]
                pk_3 = pokemon_pk_list[2]
                return self.filter(Q(pokemon=pk_1) |
                                   Q(pokemon=pk_2) |
                                   Q(pokemon=pk_3))
            case 4:
                pk_1 = pokemon_pk_list[0]
                pk_2 = pokemon_pk_list[1]
                pk_3 = pokemon_pk_list[2]
                pk_4 = pokemon_pk_list[3]
                return self.filter(Q(pokemon=pk_1) |
                                   Q(pokemon=pk_2) |
                                   Q(pokemon=pk_3) |
                                   Q(pokemon=pk_4))
            case 5:
                pk_1 = pokemon_pk_list[0]
                pk_2 = pokemon_pk_list[1]
                pk_3 = pokemon_pk_list[2]
                pk_4 = pokemon_pk_list[3]
                pk_5 = pokemon_pk_list[4]
                return self.filter(Q(pokemon=pk_1) |
                                   Q(pokemon=pk_2) |
                                   Q(pokemon=pk_3) |
                                   Q(pokemon=pk_4) |
                                   Q(pokemon=pk_5))
            case 6:
                pk_1 = pokemon_pk_list[0]
                pk_2 = pokemon_pk_list[1]
                pk_3 = pokemon_pk_list[2]
                pk_4 = pokemon_pk_list[3]
                pk_5 = pokemon_pk_list[4]
                pk_6 = pokemon_pk_list[5]
                return self.filter(Q(pokemon=pk_1) |
                                   Q(pokemon=pk_2) |
                                   Q(pokemon=pk_3) |
                                   Q(pokemon=pk_4) |
                                   Q(pokemon=pk_5) |
                                   Q(pokemon=pk_6))
