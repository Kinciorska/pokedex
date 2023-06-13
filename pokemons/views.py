from django.shortcuts import render, redirect, reverse
from urllib.parse import urljoin
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView

import requests

from .forms import SearchPokemonForm


class PokemonView(View):
    template_name = "pokemons/pokemon.html"

    def get(self, request, id_or_name):
        url = urljoin('https://pokeapi.co/api/v2/pokemon/', id_or_name)
        pokemon = requests.get(url).json()
        """The context is a dictionary mapping template variable names to Python objects."""
        context = {"pokemon": pokemon}
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