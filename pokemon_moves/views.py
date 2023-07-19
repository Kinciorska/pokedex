from django.views.generic.base import TemplateView
from urllib.parse import urljoin

import requests


from pokemons.utils import POKE_API_ENDPOINT, MOVES


class PokemonMovesView(TemplateView):
    template_name = 'pokemon_moves/pokemon_moves.html'

    def get_context_data(self, **kwargs):
        url = urljoin(POKE_API_ENDPOINT, MOVES)
        pokemon_moves = requests.get(url).json()
        context = super().get_context_data(**kwargs)
        context['moves_list'] = pokemon_moves['results']
        return context


class PokemonMoveDetailView(TemplateView):
    template_name = 'pokemon_moves/move_detail.html'

    def get_context_data(self, id_or_name, **kwargs):
        url = urljoin(POKE_API_ENDPOINT + MOVES, id_or_name)
        pokemon_move = requests.get(url).json()
        context = super().get_context_data(**kwargs)
        context['name'] = pokemon_move['name']
        context['accuracy'] = pokemon_move['accuracy']
        context['power'] = pokemon_move['power']
        context['pp'] = pokemon_move['pp']
        context['type'] = pokemon_move['type']
        context['class'] = pokemon_move['damage_class']
        context['flavor_text_list'] = pokemon_move['flavor_text_entries']
        return context
