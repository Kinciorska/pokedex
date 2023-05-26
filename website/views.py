from django.shortcuts import render
import requests
from django.views import View


class HomePageView(View):
    template_name = 'website/home.html'

    def get(self, request):
        pokemon_list_url = 'https://pokeapi.co/api/v2/pokemon/?limit=20'
        pokemon_list = requests.get(pokemon_list_url).json()
        next_pokemons = pokemon_list['next']
        print(next_pokemons)
        previous_pokemons = pokemon_list['previous']
        pokemon_list = pokemon_list['results']
        context = {"pokemon_list": pokemon_list,
                   "next_pokemons": next_pokemons,
                   "previous_pokemons": previous_pokemons,
                   }
        return render(request, self.template_name, context)
