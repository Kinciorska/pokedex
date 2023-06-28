from django.shortcuts import render, redirect
from urllib.parse import urljoin
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import requests

from .forms import SearchPokemonForm
from .models import FavouritePokemon


def set_as_favourite(id_or_name):
    return FavouritePokemon.objects.filter(name=id_or_name).exists()


class PokemonView(View):
    template_name = "pokemons/pokemon.html"

    def get(self, request, id_or_name):
        url = urljoin('https://pokeapi.co/api/v2/pokemon/', id_or_name)
        pokemon = requests.get(url).json()
        """The context is a dictionary mapping template variable names to Python objects."""
        is_favourite = set_as_favourite(id_or_name)
        context = {"pokemon": pokemon,
                   "is_favourite": is_favourite,
                   }
        return render(request, self.template_name, context)


class SearchPokemonView(FormView):
    template_name = "pokemons/search.html"
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
            return redirect("pokemons:pokemon_detail", name)
        else:
            context = {"form": form}
            return render(request, self.template_name, context)


class AddFavouritePokemon(View):
    model = FavouritePokemon

    @method_decorator(login_required(login_url="/website/login/"))
    def get(self, request, id_or_name):
        user = request.user
        favourite_pokemon = self.model(name=id_or_name, user=user)
        favourite_pokemon.save()
        return redirect("pokemons:pokemon_detail", id_or_name)


class RemoveFavouritePokemon(View):
    model = FavouritePokemon

    @method_decorator(login_required(login_url="/website/login/"))
    def get(self, request, id_or_name):
        user = request.user
        favourite_pokemon = self.model.objects.filter(name=id_or_name)
        favourite_pokemon.delete()
        return redirect("pokemons:pokemon_detail", id_or_name)


class FavouritePokemonView(ListView):
    model = FavouritePokemon
    template_name = "pokemons/favourite_pokemon.html"
