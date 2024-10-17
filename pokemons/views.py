import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.base import TemplateView

from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from urllib.parse import urljoin

from .utils import get_pokemon_id, get_move_details, get_missing_number, POKE_API_ENDPOINT, POKEMON, MOVES, TYPES
from .forms import SearchPokemonForm, AddToTeamForm, RemoveFromTeamForm, AddToFavouritesForm, AddMoveForm, \
    RemoveMoveForm
from .models import Pokemon, FavouritePokemon, Team, Move, UserPokemonMoves
from .serializers import PokemonSerializer, TeamSerializer, PokemonMovesSerializer, FavouritePokemonSerializer, \
    MoveSerializer


class HomePageView(ListView):
    """View class displaying all Pokémon, paginated by 20 per page."""

    template_name = 'pokemons/home.html'
    paginate_by = 20
    model = Pokemon


class PokemonView(View):
    """View class displaying information about a Pokémon and customization options."""

    template_name = 'pokemons/pokemon.html'
    model = Pokemon

    def get(self, request, id_or_name):
        """Returns information about a Pokémon and the forms to assign and un-assign moves, add to team and add to favourites."""

        url = urljoin(POKE_API_ENDPOINT + POKEMON, id_or_name)
        pokemon = requests.get(url).json()
        is_favourite = False
        team_full = False
        moves_full = False
        move_names = []

        if request.user.is_authenticated:
            user = request.user
            pokemon_id = pokemon['id']
            pokemon_object = self.model.objects.get(pokemon_id=pokemon_id)
            pokemon_pk = getattr(pokemon_object, 'id')
            is_favourite = FavouritePokemon.objects.filter(pokemon=pokemon_object, user=user).exists()
            team_full = Team.objects.filter(user=user).count() == 6
            moves_full = UserPokemonMoves.objects.filter(user=user, pokemon_id=pokemon_pk).count() == 4
            move_names = self.get_chosen_moves_list(user, pokemon_object)

        context = {'pokemon': pokemon,
                   'pokemon_types_list': pokemon['types'],
                   'pokemon_abilities_list': pokemon['abilities'],
                   'pokemon_moves_list': pokemon['moves'],
                   'move_names': move_names,
                   'is_favourite': is_favourite,
                   'team_full': team_full,
                   'moves_full': moves_full,
                   'team_form': AddToTeamForm,
                   'favourite_form': AddToFavouritesForm,
                   'add_move_form': AddMoveForm,
                   'remove_move_form': RemoveMoveForm,
                   }
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='/website/login/'))
    def save_in_team(self, request, pokemon_id):
        """Saves the given Pokémon in the team of the user, if there are 6 Pokémon already, it returns an error."""

        user = request.user
        existing_numbers = Team.objects.filter(user=user).values_list('pokemon_number', flat=True)

        if existing_numbers.count() == 6:
            messages.error(request, "There are already 6 Pokémon in your team")
            return
        missing_number = get_missing_number(numbers=set(range(1, 7)), existing_numbers=existing_numbers)
        team = Team(user=user, pokemon_number=missing_number)
        team.save()
        pokemon = self.model.objects.get(pokemon_id=pokemon_id)
        team.pokemon.add(pokemon)
        return

    @staticmethod
    def save_in_favourites(request, pokemon_id):
        """Saves the given Pokémon as favourite for the user."""

        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
        pokemon_in_favourites = FavouritePokemon(user=request.user, pokemon=pokemon)
        pokemon_in_favourites.save()
        return

    @staticmethod
    def get_move_number(request, pokemon):
        """
        Returns the first number available for saving a move for a Pokémon, when there are 4 moves already assigned
        it returns an error.
        """
        existing_numbers = (UserPokemonMoves.objects.filter(user=request.user, pokemon=pokemon)).values_list(
            'move_number',
            flat=True)
        match existing_numbers.count():

            case 0 | 1 | 2 | 3:
                missing_number = get_missing_number(numbers=set(range(1, 5)), existing_numbers=existing_numbers)
                return missing_number
            case 4:
                messages.error(request, "There are already 4 moves assigned for this Pokémon")
                return

    @staticmethod
    def get_chosen_moves_list(user, pokemon_pk):
        """Returns the list of moves assigned to a Pokémon."""

        move_numbers = UserPokemonMoves.objects.filter(user=user, pokemon_id=pokemon_pk).values_list('move_id',
                                                                                                     flat=True)
        move_names_query = Move.objects.filter(pk__in=move_numbers).all()
        move_names = [str(name) for name in move_names_query]
        return move_names

    @method_decorator(login_required(login_url='/website/login/'))
    def add_move(self, request, pokemon_id):
        """Adds a move to a specified Pokémon, if there are 4 moves assigned already, it returns an error."""

        user = request.user
        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
        move_name = request.POST['move_name']
        move_details = get_move_details(move_name)
        move = Move.objects.get_or_create(
            move_id=move_details[0],
            move_name=move_name,
            move_type=move_details[1]
        )
        move = move[0]
        number = self.get_move_number(request, pokemon)
        if UserPokemonMoves.objects.filter(user=user, pokemon=pokemon, move=move).exists():
            messages.error(request, "This move is already assigned to this pokemon")
            return
        pokemon_move = UserPokemonMoves(user=user, move_number=number, pokemon=pokemon, move=move)
        pokemon_move.save()
        return

    @method_decorator(login_required(login_url='/website/login/'))
    def remove_move(self, request, pokemon_id):
        """Removes a move from a specified Pokémon."""

        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
        move_name = request.POST['move_name']
        move = get_object_or_404(Move, move_name=move_name)
        pokemon_move = UserPokemonMoves.objects.get(user=request.user, pokemon=pokemon, move=move)
        pokemon_move.delete()
        return

    @method_decorator(login_required(login_url='/website/login/'))
    def post(self, request, id_or_name):
        """
        Depending on the form name provided from the Pokémon detail view page, it adds the Pokémon to the user's team,
        adds it to favourites or assign and un-assign moves to a Pokémon.
        """
        query_dict = request.POST.dict()
        query = list(query_dict)
        form = query[2]

        match form:

            case 'team_form' if AddToTeamForm(request.POST).is_valid():
                pokemon_id = get_pokemon_id(id_or_name)
                self.save_in_team(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'favourite_form' if AddToTeamForm(request.POST).is_valid():
                pokemon_id = get_pokemon_id(id_or_name)
                self.save_in_favourites(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'add_move_form':
                pokemon_id = get_pokemon_id(id_or_name)
                self.add_move(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'remove_move_form':
                pokemon_id = get_pokemon_id(id_or_name)
                self.remove_move(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case [_]:
                team_form = AddToTeamForm(request.POST)
                favourite_form = AddToTeamForm(request.POST)
                add_move_form = AddMoveForm(request.POST)
                remove_move_form = RemoveMoveForm(request.POST)
                context = {'favourite_form': favourite_form,
                           'team_form': team_form,
                           'add_move_form': add_move_form,
                           'remove_move_form': remove_move_form,
                           }
                return render(request, self.template_name, context)


class PokemonTeamView(LoginRequiredMixin, View):
    """View class displaying information about Pokémon saved by the user in their team."""

    model = Team
    template_name = 'pokemons/pokemon_team.html'

    @staticmethod
    def get_move(user, pokemon_pk, move_number):
        """
        Returns the name of the move of the given Pokémon, if no move is assigned to it returns an empty string.
        """
        try:
            pokemon_move = UserPokemonMoves.objects.get(user=user, pokemon_id=pokemon_pk, move_number=move_number)
            move = pokemon_move.move
        except ObjectDoesNotExist:
            move = ''
        return move

    def get(self, request):
        """Returns the number, name, types and moves of Pokémon saved in the user's team."""

        user = request.user
        all_pokemons = (self.model.objects.filter(user=user))
        pokemon_pk_list = list(self.model.objects.filter(user=user).values_list('pokemon', flat=True))
        context = {
            'pokemon_number_list': list(all_pokemons.values_list('pokemon_number', flat=True)),
            'pokemon_id_list': [getattr(Pokemon.objects.get(id=pk), 'pokemon_id') for pk in pokemon_pk_list],
            'pokemon_name_list': [getattr(Pokemon.objects.get(id=pk), 'pokemon_name') for pk in pokemon_pk_list],
            'pokemon_type_1_list': [getattr(Pokemon.objects.get(id=pk), 'pokemon_type_1') for pk in pokemon_pk_list],
            'pokemon_type_2_list': [getattr(Pokemon.objects.get(id=pk), 'pokemon_type_2') for pk in pokemon_pk_list],
            'pokemon_move1_list': [self.get_move(user, pokemon_pk, 1) for pokemon_pk in pokemon_pk_list],
            'pokemon_move2_list': [self.get_move(user, pokemon_pk, 2) for pokemon_pk in pokemon_pk_list],
            'pokemon_move3_list': [self.get_move(user, pokemon_pk, 3) for pokemon_pk in pokemon_pk_list],
            'pokemon_move4_list': [self.get_move(user, pokemon_pk, 4) for pokemon_pk in pokemon_pk_list],
            'team_form': RemoveFromTeamForm,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Removes the given Pokémon from the user's team."""

        pokemon_number = int(request.POST.get('pokemon_number'))
        team_pk = self.model.objects.get(user=request.user, pokemon_number=pokemon_number)
        team_pk.delete()
        return redirect('pokemons:pokemon_team')


class SearchPokemonView(FormView):
    """View form allowing to search for a Pokémon using its name or id."""

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


class FavouritePokemonView(LoginRequiredMixin, View):
    """View class displaying Pokémon saved as favourites by the user."""

    model = FavouritePokemon
    template_name = 'pokemons/favourite_pokemon.html'

    def get(self, request):
        pokemons = (self.model.objects.filter(user=request.user))
        context = {'pokemons': pokemons}
        return render(request, self.template_name, context)

    def post(self, request):
        """Removes the given Pokémon from the user's favourites."""

        pokemon_id = int(request.POST.get('pokemon_id'))
        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
        favourite_pokemon = self.model.objects.get(user=request.user, pokemon=pokemon)
        favourite_pokemon.delete()
        return redirect('pokemons:favourite_pokemon')


class PokemonViewSet(viewsets.ModelViewSet):
    """API endpoint that allows a Pokémon to be viewed."""

    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer
    permission_classes = [permissions.AllowAny]


class FavouritePokemonViewSet(viewsets.ModelViewSet):
    """API endpoint that allows to view Pokémon set as favourite."""

    serializer_class = FavouritePokemonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """This view should return all the Pokémon set as favourites by the user."""
        favourite_pokemons = FavouritePokemon.objects.filter(user=self.request.user)
        return favourite_pokemons


class TeamMovesList(ListAPIView):
    """API endpoint that allows to view the Pokémon added to the team, and their assigned moves."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class_Team = TeamSerializer

    @staticmethod
    def get_queryset_team(user):
        """This queryset should return all the Pokémon in the team of the user."""

        return Team.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        team = self.serializer_class_Team(self.get_queryset_team(user), many=True)
        data = {'Team': team.data}
        return Response(data)


class MovesView(View):
    """View class displaying all moves, paginated by 30 per page."""

    template_name = 'pokemons/pokemon_moves.html'
    paginate_by = 30

    def get(self, request):
        move_list_url = urljoin(POKE_API_ENDPOINT + MOVES, '?limit=-1')
        move_list_json = requests.get(move_list_url).json()
        move_list = move_list_json['results']
        pokemon_paginator = Paginator(move_list, self.paginate_by)
        page_number = request.GET.get("page")
        page_obj = pokemon_paginator.get_page(page_number)
        return render(request, self.template_name, {"page_obj": page_obj})


class MoveDetailView(View):
    """View class displaying information about a move."""

    template_name = 'pokemons/move_detail.html'

    def get(self, request, id_or_name):
        url = urljoin(POKE_API_ENDPOINT + MOVES, id_or_name)
        pokemon_move = requests.get(url).json()
        context = {'name': pokemon_move['name'],
                   'accuracy': pokemon_move['accuracy'],
                   'power': pokemon_move['power'],
                   'pp': pokemon_move['pp'],
                   'type': pokemon_move['type'],
                   'class': pokemon_move['damage_class'],
                   'flavor_text_list': pokemon_move['flavor_text_entries'],
                   }
        return render(request, self.template_name, context)


class MoveViewSet(viewsets.ModelViewSet):
    """API endpoint that allows all moves to be viewed."""

    queryset = Move.objects.all()
    serializer_class = MoveSerializer
    permission_classes = [permissions.AllowAny]


class UserPokemonMovesList(APIView):
    """API endpoint that allows to view the Pokémon and their assigned moves."""

    model = Pokemon
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """This view should return a list of all the Pokémon and their moves, filtered by the current user."""

        pokemon_moves = self.model.objects.has_moves(request.user)
        serialized_pokemon_moves = PokemonMovesSerializer(pokemon_moves, many=True)
        return Response(serialized_pokemon_moves.data)


class PokemonTypeDetailView(TemplateView):
    """View class displaying information about a type."""

    template_name = 'pokemons/type_details.html'

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
    """View class displaying all types"""

    template_name = 'pokemons/pokemon_types.html'

    def get_context_data(self, **kwargs):
        url = urljoin(POKE_API_ENDPOINT, TYPES)
        pokemon_types = requests.get(url).json()
        context = super().get_context_data(**kwargs)
        context['type_list'] = pokemon_types['results']
        return context
