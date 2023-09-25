from django.shortcuts import render, redirect, get_object_or_404
from urllib.parse import urljoin
from django.contrib import messages
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import requests
from django.views.generic import View
from .utils import POKE_API_ENDPOINT, POKEMON
from .forms import SearchPokemonForm, AddToTeamForm, RemoveFromTeamForm, AddToFavouritesForm, RemoveFromFavouritesForm
from .models import FavouritePokemon, Team, Pokemon


class HomePageView(TemplateView):
    template_name = 'pokemons/home.html'

    def get_context_data(self, **kwargs):
        pokemon_list_url = urljoin(POKE_API_ENDPOINT + POKEMON, '?limit=20')
        pokemon_list = requests.get(pokemon_list_url).json()
        context = super().get_context_data(**kwargs)
        context["pokemon_list"] = pokemon_list['results']
        context["next_pokemons"] = pokemon_list['next']
        context["previous_pokemons"] = pokemon_list['previous']
        return context


class PokemonView(View):
    template_name = 'pokemons/pokemon.html'
    model = Pokemon

    def get(self, request, id_or_name):
        url = urljoin(POKE_API_ENDPOINT + POKEMON, id_or_name)
        pokemon = requests.get(url).json()
        pokemon_id = pokemon['id']
        pokemon_types_list = pokemon['types']
        pokemon_abilities_list = pokemon['abilities']
        pokemon_moves_list = pokemon['moves']
        is_favourite = False
        team_full = False
        if request.user.is_authenticated:
            user = request.user
            pokemon_data = self.get_pokemon_data(pokemon_id)
            pokemon_name = pokemon_data[0]
            pokemon_type_1 = pokemon_data[1]
            pokemon_type_2 = pokemon_data[2]
            saved_pokemon = Pokemon.objects.get_or_create(
                pokemon_id=pokemon_id,
                pokemon_name=pokemon_name,
                pokemon_type_1=pokemon_type_1,
                pokemon_type_2=pokemon_type_2,
            )
            saved_pokemon = saved_pokemon[0]
            is_favourite = FavouritePokemon.objects.filter(pokemon=saved_pokemon, user=user).exists()
            team_full = Team.objects.filter(user=user).count() == 6

        context = {'pokemon': pokemon,
                   'pokemon_types_list': pokemon_types_list,
                   'pokemon_abilities_list': pokemon_abilities_list,
                   'pokemon_moves_list': pokemon_moves_list,
                   'is_favourite': is_favourite,
                   'team_full': team_full,
                   'team_form': AddToTeamForm,
                   'favourite_form': AddToFavouritesForm,
                   }
        return render(request, self.template_name, context)

    def get_pokemon_data(self, pokemon_id):
        url = urljoin(POKE_API_ENDPOINT + POKEMON, str(pokemon_id))
        pokemon = requests.get(url).json()
        pokemon_name = pokemon['name']
        pokemon_type1 = pokemon['types'][0]['type']['name']
        try:
            pokemon_type2 = pokemon['types'][1]['type']['name']
        except IndexError:
            pokemon_type2 = ''
        return pokemon_name, pokemon_type1, pokemon_type2


    @method_decorator(login_required(login_url='/website/login/'))
    def save_in_team(self, request, pokemon_id):
        user = request.user
        existing_numbers = (Team.objects.filter(user=user)).values_list('pokemon_number', flat=True)
        if existing_numbers.count() != 6:
            numbers = set(range(1, 7))
            missing_number = list(numbers - set(existing_numbers))[0]
            pokemon_in_team = Team(user=user, pokemon_number=missing_number)
            pokemon_in_team.save()
            pokemon = Pokemon.objects.get(pokemon_id=pokemon_id)
            pokemon_in_team.pokemon_id.add(pokemon)
            return
        # if Team.objects.filter(user=user).count() != 6:
        #     for pokemon_counter in range(1, 7):
        #         print(pokemon_counter)
        #         if not Team.objects.filter(user=user, pokemon_number=pokemon_counter).exists():
        #             pokemon_number = pokemon_counter
        #             pokemon_in_team = Team(user=user, pokemon_number=pokemon_number)
        #             pokemon_in_team.save()
        #             pokemon = Pokemon.objects.get(pokemon_id=pokemon_id)
        #             pokemon_in_team = Team.objects.get(user=user, pokemon_number=pokemon_counter)
        #             pokemon_in_team.pokemon_id.add(pokemon)
        #             if pokemon_counter == pokemon_number:
        #                 break
        #     return
        messages.error(request, "There are already 6 pokemons in your team")
        return
    def post(self, request, id_or_name):
        query_dict = request.POST.dict()
        query = list(query_dict)
        form = query[2]

        match form:

            case "team_form" if AddToTeamForm(request.POST).is_valid():
                pokemon_id = get_pokemon_id(id_or_name)
                self.save_in_team(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case "favourite_form" if AddToTeamForm(request.POST).is_valid():
                user = request.user
                pokemon_id = get_pokemon_id(id_or_name)
                pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
                pokemon_in_favourites = FavouritePokemon(user=user, pokemon=pokemon)
                pokemon_in_favourites.save()
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case [_]:
                team_form = AddToTeamForm(request.POST)
                favourite_form = AddToTeamForm(request.POST)
                context = {'favourite_form': favourite_form,
                           'team_form': team_form,
                           }
                return render(request, self.template_name, context)

def get_pokemon_id(id_or_name):
    url = urljoin(POKE_API_ENDPOINT + POKEMON, id_or_name)
    pokemon = requests.get(url).json()
    pokemon_id = pokemon['id']
    return pokemon_id


class PokemonTeamView(View):
    template_name = 'pokemons/pokemon_team.html'

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request):
        user = request.user
        all_pokemons = (Team.objects.filter(user=user))
        pokemon_number_list = []
        pokemon_id_list = []
        pokemon_name_list = []
        pokemon_type_1_list = []
        pokemon_type_2_list = []
        for pokemon in all_pokemons:
            pokemons_in_team = pokemon.pokemon_id.all().values()
            pokemons_in_team = pokemons_in_team[0]
            pokemon_id = pokemons_in_team['pokemon_id']
            pokemon_id_list.append(pokemon_id)
            pokemon_name = pokemons_in_team['pokemon_name']
            pokemon_name_list.append(pokemon_name)
            pokemon_type_1 = pokemons_in_team['pokemon_type_1']
            pokemon_type_1_list.append(pokemon_type_1)
            pokemon_type_2 = pokemons_in_team['pokemon_type_2']
            pokemon_type_2_list.append(pokemon_type_2)
            pokemon_number = pokemon.pokemon_number
            pokemon_number_list.append(pokemon_number)
        context = {
            'pokemon_number_list': pokemon_number_list,
            'pokemon_id_list': pokemon_id_list,
            'pokemon_name_list': pokemon_name_list,
            'pokemon_type_1_list': pokemon_type_1_list,
            'pokemon_type_2_list': pokemon_type_2_list,
            'team_form': RemoveFromTeamForm,
            }
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='/website/login/'))
    def post(self, request):
        user = request.user
        pokemon_number = request.POST.get('pokemon_number')
        pokemon_number = int(pokemon_number)
        team_pk = Team.objects.get(user=user, pokemon_number=pokemon_number)
        team_pk.delete()
        return redirect('pokemons:pokemon_team')


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

        context = {'form': form}
        return render(request, self.template_name, context)


class FavouritePokemonView(ListView):
    model = FavouritePokemon
    template_name = 'pokemons/favourite_pokemon.html'

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request):
        user = request.user
        pokemons = (FavouritePokemon.objects.filter(user=user))
        context = {'pokemons': pokemons}
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='/website/login/'))
    def post(self, request):
        user = request.user
        pokemon_id = request.POST.get('pokemon_id')
        pokemon_id = int(pokemon_id)
        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
        favourite_pokemon = FavouritePokemon.objects.get(user=user, pokemon=pokemon)
        favourite_pokemon.delete()
        return redirect('pokemons:favourite_pokemon')

class AddMoveToPokemonView(View):
    model = Pokemon

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request, pokemon, move):
        user = request.user
        if self.model.objects.filter(user=user,name=pokemon).count() != 4:
            for move_counter in range(4):
                if not self.model.objects.filter(move_number=move_counter):
                    move_number = move_counter
            move = self.model(name=pokemon, user=user, move=move, move_number=move_number)
            move.save()
            return redirect('pokemons:pokemon_detail', pokemon)
        else:
            messages.error(request, "You already chose 4 moves for this pokemon")
            return redirect('pokemons:pokemon_detail', pokemon)