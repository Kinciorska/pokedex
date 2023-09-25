from django.views.generic.base import TemplateView
from urllib.parse import urljoin

import requests


from pokemons.utils import POKE_API_ENDPOINT, TYPES


class PokemonTypeDetailView(TemplateView):
    template_name = 'pokemon_types/type_details.html'

    def get_context_data(self, id_or_name, **kwargs):
        url = urljoin(POKE_API_ENDPOINT + TYPES, id_or_name)
        pokemon_types = requests.get(url).json()
        context = super().get_context_data(**kwargs)
        context['type_name'] = pokemon_types['name']
        context['pokemons_in_type'] = pokemon_types['pokemon']
        context['moves_in_type'] = pokemon_types['moves']
        context['double_damage_from'] = pokemon_types['damage_relations']['double_damage_from']
        context['double_damage_to'] = pokemon_types['damage_relations']['double_damage_to']
        context['half_damage_from'] = pokemon_types['damage_relations']['half_damage_from']
        context['half_damage_to'] = pokemon_types['damage_relations']['half_damage_to']
        context['no_damage_from'] = pokemon_types['damage_relations']['no_damage_from']
        context['no_damage_to'] = pokemon_types['damage_relations']['no_damage_to']
        return context


class PokemonTypesView(TemplateView):
    template_name = 'pokemon_types/pokemon_types.html'

    def get_context_data(self, **kwargs):
        url = urljoin(POKE_API_ENDPOINT, TYPES)
        pokemon_types = requests.get(url).json()
        print(pokemon_types)
        context = super().get_context_data(**kwargs)
        context['type_list'] = pokemon_types['results']
        return context

