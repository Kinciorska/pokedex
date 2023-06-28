from django.shortcuts import render, redirect
from urllib.parse import urljoin
from django.views import View
from django.contrib import messages
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import requests

from .utils import POKE_API_ENDPOINT_POKEMON
from .forms import SearchPokemonForm
from .models import FavouritePokemon, PokemonInTeam


class PokemonView(View):
    template_name = 'pokemons/pokemon.html'

    def get(self, request, id_or_name):
        url = urljoin(POKE_API_ENDPOINT_POKEMON, id_or_name)
        pokemon = requests.get(url).json()
        if request.user.is_authenticated:
            user = request.user
            is_favourite = FavouritePokemon.objects.filter(name=id_or_name).exists()
            team_full = PokemonInTeam.objects.filter(user=user).count() == 6
            is_set_to_team = PokemonInTeam.objects.filter(name=id_or_name).exists()

        context = {'pokemon': pokemon,
                   'is_favourite': is_favourite,
                   'team_full': team_full,
                   'is_set_to_team': is_set_to_team,
                   }
        return render(request, self.template_name, context)


class SearchPokemonView(FormView):
    template_name = 'pokemons/search.html'
    form_class = SearchPokemonForm

    def form_valid(self, form):
        name = form.cleaned_data
        name = name['id_or_name']
        return super(name, self).form_valid(form)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            name = form.cleaned_data
            name = name['id_or_name']
            return redirect('pokemons:pokemon_detail', name)
        else:
            context = {'form': form}
            return render(request, self.template_name, context)


class AddFavouritePokemonView(View):
    model = FavouritePokemon

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request, id_or_name):
        user = request.user
        favourite_pokemon = self.model(name=id_or_name, user=user)
        favourite_pokemon.save()
        return redirect('pokemons:pokemon_detail', id_or_name)


class RemoveFavouritePokemonView(View):
    model = FavouritePokemon

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request, id_or_name):
        user = request.user
        favourite_pokemon = self.model.objects.filter(name=id_or_name)
        favourite_pokemon.delete()
        return redirect('pokemons:pokemon_detail', id_or_name)


class FavouritePokemonView(ListView):
    model = FavouritePokemon
    template_name = 'pokemons/favourite_pokemon.html'


class PokemonTeamView(ListView):
    model = PokemonInTeam
    template_name = 'pokemons/pokemon_team.html'


class AddPokemonToTeamView(View):
    model = PokemonInTeam

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request, id_or_name):
        pokemon_counter = 0
        user = request.user
        if PokemonInTeam.objects.filter(user=user).count() != 6:
            for pokemon_counter in range(6):
                if not self.model.objects.filter(number=pokemon_counter):
                    number = pokemon_counter
            pokemon_in_team = self.model(name=id_or_name, user=user, number=number)
            pokemon_in_team.save()
            return redirect('pokemons:pokemon_detail', id_or_name)
        else:
            messages.error(request, "There are already 6 pokemons in your team")
            return redirect('pokemons:pokemon_detail', id_or_name)


class RemovePokemonFromTeamView(View):
    model = PokemonInTeam

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request, id_or_name):
        user = request.user
        pokemon_in_team = self.model.objects.filter(name=id_or_name)
        pokemon_in_team.delete()
        return redirect('pokemons:pokemon_detail', id_or_name)
