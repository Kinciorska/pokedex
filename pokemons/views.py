import requests

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from rest_framework import permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from requests import RequestException
from urllib.parse import urljoin

from .utils import get_pokemon_id, get_move_details, get_missing_number, POKE_API_ENDPOINT, POKEMON, MOVES, TYPES
from .forms import SearchPokemonForm, AddToTeamForm, RemoveFromTeamForm, AddToFavouritesForm, AddMoveForm, \
    RemoveMoveForm
from .models import Pokemon, FavouritePokemon, Team, Move, UserPokemonMoves
from .serializers import PokemonSerializer, TeamSerializer, PokemonMovesSerializer, FavouritePokemonSerializer, \
    MoveSerializer
from pokedex.settings import logger


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

        try:
            pokemon = self._fetch_pokemon(id_or_name)

            if not pokemon:
                messages.error(request, "No Pokémon found.")
                return redirect('pokemons:home')

            pokemon = pokemon.json()

            context = {'pokemon': pokemon,
                       'pokemon_types_list': pokemon['types'],
                       'pokemon_abilities_list': pokemon['abilities'],
                       'pokemon_moves_list': pokemon['moves'],
                       'team_form': AddToTeamForm,
                       'favourite_form': AddToFavouritesForm,
                       'add_move_form': AddMoveForm,
                       'remove_move_form': RemoveMoveForm,
                       'is_favourite': False,
                       'team_full': False,
                       'moves_full': False,
                       'move_names': []}

            user_context = self._get_user_context(request, pokemon['id']) if request.user.is_authenticated else {}
            context.update(user_context)

            return render(request, self.template_name, context)

        except requests.JSONDecodeError as e:

            logger.error(f"Error {e} with Pokémon {id_or_name}")
            messages.error(request, "No Pokémon found. Check the spelling and try again.")

            return redirect('pokemons:home')

    @staticmethod
    def _fetch_pokemon(id_or_name):
        """Fetches Pokémon data from the API by ID or name."""
        url = urljoin(POKE_API_ENDPOINT + POKEMON, id_or_name)
        try:
            response = requests.get(url)
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            return None

    def _get_user_context(self, request, pokemon_id):
        user = request.user

        try:
            pokemon_object = self.model.objects.get(pokemon_id=pokemon_id)
            pokemon_pk = getattr(pokemon_object, 'id')

            return {'is_favourite': FavouritePokemon.objects.filter(pokemon=pokemon_object, user=user).exists(),
                    'team_full': Team.objects.filter(user=user).count() >= 6,
                    'moves_full': UserPokemonMoves.objects.filter(user=user, pokemon_id=pokemon_pk).count() >= 4,
                    'move_names': self._get_chosen_moves_list(user, pokemon_object)}

        except self.model.DoesNotExist:
            logger.error(f"Pokémon with ID {pokemon_id} not found in the database.")
            return {}

    @method_decorator(login_required(login_url='/website/login/'))
    def _save_in_team(self, request, pokemon_id):
        """Saves the given Pokémon in the team of the user, if there are 6 Pokémon already, it returns an error."""

        user = request.user
        try:
            with transaction.atomic():
                existing_numbers = Team.objects.filter(user=user).values_list('pokemon_number', flat=True)

                if existing_numbers.count() == 6:
                    messages.error(request, "There are already 6 Pokémon in your team")
                    return

                missing_number = get_missing_number(numbers=set(range(1, 7)), existing_numbers=existing_numbers)
                team = Team.objects.create(user=user, pokemon_number=missing_number)
                pokemon = self.model.objects.get(pokemon_id=pokemon_id)
                team.pokemon.add(pokemon)
                return

        except ObjectDoesNotExist:
            logger.error(f"Error saving Pokémon with ID {pokemon_id} to team")
            messages.error(request, "Error saving Pokémon to your team.")
            return redirect('pokemons:home')

    @staticmethod
    def _save_in_favourites(request, pokemon_id):
        """Saves the given Pokémon as favourite for the user."""

        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)

        if FavouritePokemon.objects.filter(user=request.user, pokemon=pokemon).exists():
            messages.info(request, "Pokémon already saved to favourites.")
            return

        pokemon_in_favourites = FavouritePokemon(user=request.user, pokemon=pokemon)
        pokemon_in_favourites.save()
        return

    @staticmethod
    def _get_move_number(request, pokemon):
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
    def _get_chosen_moves_list(user, pokemon_pk):
        """Returns the list of moves assigned to a Pokémon."""

        moves = (
            UserPokemonMoves.objects.filter(user=user, pokemon_id=pokemon_pk)
            .select_related('move')
        )

        return [move.move.move_name for move in moves]

    @method_decorator(login_required(login_url='/website/login/'))
    def _add_move(self, request, pokemon_id):
        """Adds a move to a specified Pokémon"""

        user = request.user
        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
        move_name = request.POST['move_name']
        move_id, move_type = get_move_details(move_name)

        if not move_id:
            messages.error(request, "Something went wrong, move not added.")
            return

        move, created = Move.objects.get_or_create(
            move_id=move_id,
            move_name=move_name,
            move_type=move_type
        )

        if UserPokemonMoves.objects.filter(user=user, pokemon=pokemon, move=move).exists():
            messages.error(request, "This move is already assigned to this pokemon")
            return

        number = self._get_move_number(request, pokemon)
        pokemon_move = UserPokemonMoves(user=user, move_number=number, pokemon=pokemon, move=move)
        pokemon_move.save()

        return

    @method_decorator(login_required(login_url='/website/login/'))
    def _remove_move(self, request, pokemon_id):
        """Removes a move from a specified Pokémon."""

        move_name = request.POST['move_name']

        try:
            pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
            move = get_object_or_404(Move, move_name=move_name)
            pokemon_move = UserPokemonMoves.objects.get(user=request.user, pokemon=pokemon, move=move)
            pokemon_move.delete()
            return

        except Pokemon.DoesNotExist:
            logger.error(f"Removing move {move_name} failed, Pokémon with id {pokemon_id} does not exist")
            messages.error(request, "The Pokémon you are trying to modify does not exist.")

            return

        except Move.DoesNotExist:
            logger.error(f"Removing move {move_name} failed, move {move_name} does not exist")
            messages.error(request, "The move you are trying to modify does not exist.")

            return

        except UserPokemonMoves.DoesNotExist:
            logger.error(f"Removing move {move_name} failed, UserPokemonMove object with pokemon id {pokemon_id} "
                         f"and move {pokemon_move} does not exist.")
            messages.error(request, "The specified move is not associated with this Pokémon.")

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
                self._save_in_team(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'favourite_form' if AddToTeamForm(request.POST).is_valid():
                pokemon_id = get_pokemon_id(id_or_name)
                self._save_in_favourites(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'add_move_form':
                pokemon_id = get_pokemon_id(id_or_name)
                self._add_move(request, pokemon_id)
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'remove_move_form':
                pokemon_id = get_pokemon_id(id_or_name)
                self._remove_move(request, pokemon_id)
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
    def _get_move(user, pokemon_pk, move_number, default=''):
        """
        Returns the name of the move of the given Pokémon, if no move is assigned to it returns an empty string.
        """
        try:
            pokemon_move = UserPokemonMoves.objects.get(user=user, pokemon_id=pokemon_pk, move_number=move_number)
            return pokemon_move.move

        except ObjectDoesNotExist:
            return default

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
            'pokemon_move1_list': [self._get_move(user, pokemon_pk, 1) for pokemon_pk in pokemon_pk_list],
            'pokemon_move2_list': [self._get_move(user, pokemon_pk, 2) for pokemon_pk in pokemon_pk_list],
            'pokemon_move3_list': [self._get_move(user, pokemon_pk, 3) for pokemon_pk in pokemon_pk_list],
            'pokemon_move4_list': [self._get_move(user, pokemon_pk, 4) for pokemon_pk in pokemon_pk_list],
            'team_form': RemoveFromTeamForm,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Removes the given Pokémon from the user's team."""

        pokemon_number = int(request.POST.get('pokemon_number'))
        try:
            team_pk = self.model.objects.get(user=request.user, pokemon_number=pokemon_number)
            team_pk.delete()
            return redirect('pokemons:pokemon_team')
        except ObjectDoesNotExist:
            logger.error(f"Pokemon with number {pokemon_number} not found during delete")
            return redirect('pokemons:home')


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
        url = urljoin(POKE_API_ENDPOINT + MOVES, '?limit=-1')
        try:
            move_list_json = requests.get(url).json()
            move_list = move_list_json['results']
            pokemon_paginator = Paginator(move_list, self.paginate_by)
            page_number = request.GET.get("page")
            page_obj = pokemon_paginator.get_page(page_number)
            return render(request, self.template_name, {"page_obj": page_obj})

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            return HttpResponseServerError("An error occurred during the request.")


class MoveDetailView(View):
    """View class displaying information about a move."""

    template_name = 'pokemons/move_detail.html'

    def get(self, request, id_or_name):
        url = urljoin(POKE_API_ENDPOINT + MOVES, id_or_name)
        try:
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
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            return HttpResponseServerError("An error occurred during the request.")


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
        try:
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

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            return HttpResponseServerError("An error occurred during the request.")


class PokemonTypesView(TemplateView):
    """View class displaying all types"""

    template_name = 'pokemons/pokemon_types.html'

    def get_context_data(self, **kwargs):
        url = urljoin(POKE_API_ENDPOINT, TYPES)
        try:
            pokemon_types = requests.get(url).json()
            context = super().get_context_data(**kwargs)
            context['type_list'] = pokemon_types['results']
            return context

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            return HttpResponseServerError("An error occurred during the request.")
