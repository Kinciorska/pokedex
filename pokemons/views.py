import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
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

from .utils import get_pokemon_id, get_move_details, POKE_API_ENDPOINT, POKEMON, MOVES, POKEMON_SPECIES, TYPES
from .forms import SearchPokemonForm, AddToTeamForm, RemoveFromTeamForm, AddToFavouritesForm, RemoveFromFavouritesForm, \
    AddMoveForm, RemoveMoveForm
from .models import Pokemon, FavouritePokemon, Team, Move, PokemonMoves
from .serializers import PokemonSerializer, TeamSerializer, PokemonMovesSerializer, FavouritePokemonSerializer, \
    MoveSerializer


class HomePageView(ListView):
    template_name = 'pokemons/home.html'
    paginate_by = 20
    model = Pokemon


class PokemonView(View):
    template_name = 'pokemons/pokemon.html'
    model = Pokemon

    def get(self, request, id_or_name):
        url = urljoin(POKE_API_ENDPOINT + POKEMON, id_or_name)
        pokemon = requests.get(url).json()
        pokemon_types_list = pokemon['types']
        pokemon_abilities_list = pokemon['abilities']
        pokemon_moves_list = pokemon['moves']
        is_favourite = False
        team_full = False
        moves_full = False
        move_names = []

        if request.user.is_authenticated:
            user = request.user
            pokemon_id = pokemon['id']
            pokemon = Pokemon.objects.get(pokemon_id=pokemon_id)
            pokemon_pk = getattr(pokemon, 'id')
            is_favourite = FavouritePokemon.objects.filter(pokemon=pokemon, user=user).exists()
            team_full = Team.objects.filter(user=user).count() == 6
            moves_full = PokemonMoves.objects.filter(user=user, pokemon_id=pokemon_pk).count() == 4
            move_names = self.get_chosen_moves_list(user, pokemon)

        context = {'pokemon': pokemon,
                   'pokemon_types_list': pokemon_types_list,
                   'pokemon_abilities_list': pokemon_abilities_list,
                   'pokemon_moves_list': pokemon_moves_list,
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
        messages.error(request, "There are already 6 pokemons in your team")
        return

    def get_move_number(self, request, pokemon):
        existing_numbers = (PokemonMoves.objects.filter(user=request.user, pokemon=pokemon)).values_list('move_number',
                                                                                                 flat=True)
        match existing_numbers.count():

            case 0 | 1 | 2 | 3:
                numbers = set(range(1, 5))
                missing_number = list(numbers - set(existing_numbers))[0]
                return missing_number
            case 4:
                messages.error(request, "There are already 6 pokemons in your team")
                return

    def get_chosen_moves_list(self, user, pokemon_pk):
        move_numbers = PokemonMoves.objects.filter(user=user, pokemon_id=pokemon_pk).values_list('move_id', flat=True)
        move_names_query = Move.objects.filter(pk__in=move_numbers).all()
        move_names = []
        for name in move_names_query:
            name = str(name)
            move_names.append(name)
        return move_names


    def post(self, request, id_or_name):
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
                pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
                pokemon_in_favourites = FavouritePokemon(user=request.user, pokemon=pokemon)
                pokemon_in_favourites.save()
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'add_move_form':
                user = request.user
                pokemon_id = get_pokemon_id(id_or_name)
                pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
                move_name = request.POST['move_name']
                move_details = get_move_details(move_name)
                move_id = move_details[0]
                move_type = move_details[1]
                move = Move.objects.get_or_create(
                    move_id=move_id,
                    move_name=move_name,
                    move_type=move_type,
                )
                move = move[0]
                number = self.get_move_number(request, pokemon)
                if PokemonMoves.objects.filter(user=user, pokemon=pokemon, move=move).exists():
                    messages.error(request, "This move is already assigned to this pokemon")
                    return
                pokemon_move = PokemonMoves(user=user, move_number=number, pokemon=pokemon, move=move)
                pokemon_move.save()
                return redirect('pokemons:pokemon_detail', pokemon_id)

            case 'remove_move_form':
                pokemon_id = get_pokemon_id(id_or_name)
                pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
                move_name = request.POST['move_name']
                move = get_object_or_404(Move, move_name=move_name)
                pokemon_move = PokemonMoves.objects.get(user=request.user, pokemon=pokemon, move=move)
                pokemon_move.delete()
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


class PokemonTeamView(View):
    template_name = 'pokemons/pokemon_team.html'

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request):
        user = request.user
        all_pokemons = (Team.objects.filter(user=user))
        pokemon_number = all_pokemons.values_list('pokemon_number', flat=True)
        pokemon_number_list = list(pokemon_number)
        pokemon_pk = all_pokemons.values_list('pokemon_id', flat=True)
        pokemon_pk_list = list(pokemon_pk)
        pokemon_data = {'number': pokemon_number_list,
                        'id': [],
                        'name': [],
                        'type_1': [],
                        'type_2': [],
                        'moves1': [],
                        'moves2': [],
                        'moves3': [],
                        'moves4': [],
                        }
        for pk in pokemon_pk_list:
            current_pokemon = Pokemon.objects.get(id=pk)
            pokemon_id = getattr(current_pokemon, 'pokemon_id')
            name = getattr(current_pokemon, 'pokemon_name')
            type_1 = getattr(current_pokemon, 'pokemon_type_1')
            type_2 = getattr(current_pokemon, 'pokemon_type_2')
            moves = PokemonMoves.objects.filter(user=user, pokemon_id=pk).all()
            moves_number = moves.values_list('move_number', flat=True)
            moves_number = list(moves_number)
            for number in moves_number:
                match number:
                    case 1:
                        move1 = str(moves.get(move_number=1))
                        pokemon_data['moves1'].append(move1)
                    case 2:
                        move2 = str(moves.get(move_number=2))
                        pokemon_data['moves2'].append(move2)
                    case 3:
                        move3 = str(moves.get(move_number=3))
                        pokemon_data['moves3'].append(move3)
                    case 4:
                        move4 = str(moves.get(move_number=4))
                        pokemon_data['moves4'].append(move4)
            numbers = set(range(1, 5))
            missing_numbers = list(numbers - set(moves_number))
            for number in missing_numbers:
                match number:
                    case 1:
                        move1 = ""
                        pokemon_data['moves1'].append(move1)
                    case 2:
                        move2 = ""
                        pokemon_data['moves2'].append(move2)
                    case 3:
                        move3 = ""
                        pokemon_data['moves3'].append(move3)
                    case 4:
                        move4 = ""
                        pokemon_data['moves4'].append(move4)
            pokemon_data['id'].append(pokemon_id)
            pokemon_data['name'].append(name)
            pokemon_data['type_1'].append(type_1)
            pokemon_data['type_2'].append(type_2)
        context = {
            'pokemon_number_list': pokemon_data['number'],
            'pokemon_id_list': pokemon_data['id'],
            'pokemon_name_list': pokemon_data['name'],
            'pokemon_type_1_list': pokemon_data['type_1'],
            'pokemon_type_2_list': pokemon_data['type_2'],
            'pokemon_move1_list': pokemon_data['moves1'],
            'pokemon_move2_list': pokemon_data['moves2'],
            'pokemon_move3_list': pokemon_data['moves3'],
            'pokemon_move4_list': pokemon_data['moves4'],
            'team_form': RemoveFromTeamForm,
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='/website/login/'))
    def post(self, request):
        pokemon_number = request.POST.get('pokemon_number')
        pokemon_number = int(pokemon_number)
        team_pk = Team.objects.get(user=request.user, pokemon_number=pokemon_number)
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
        pokemons = (FavouritePokemon.objects.filter(user=request.user))
        context = {'pokemons': pokemons}
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='/website/login/'))
    def post(self, request):
        pokemon_id = request.POST.get('pokemon_id')
        pokemon_id = int(pokemon_id)
        pokemon = get_object_or_404(Pokemon, pokemon_id=pokemon_id)
        favourite_pokemon = FavouritePokemon.objects.get(user=request.user, pokemon=pokemon)
        favourite_pokemon.delete()
        return redirect('pokemons:favourite_pokemon')


class AddMoveToPokemonView(View):
    model = Pokemon

    @method_decorator(login_required(login_url='/website/login/'))
    def get(self, request, pokemon, move):
        user = request.user
        if self.model.objects.filter(user=user, name=pokemon).count() != 4:
            for move_counter in range(4):
                if not self.model.objects.filter(move_number=move_counter):
                    move_number = move_counter
            move = self.model(name=pokemon, user=user, move=move, move_number=move_number)
            move.save()
            return redirect('pokemons:pokemon_detail', pokemon)
        else:
            messages.error(request, "You already chose 4 moves for this pokemon")
            return redirect('pokemons:pokemon_detail', pokemon)


class PokemonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a Pokémon to be viewed.
    """
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer
    permission_classes = [permissions.AllowAny]


class FavouritePokemonViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to view Pokémon set as favourite.
    """
    serializer_class = FavouritePokemonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the Pokémon set as
        favourites by the user.
        """
        favourite_pokemons = FavouritePokemon.objects.filter(user=self.request.user)
        return favourite_pokemons


class TeamMovesList(ListAPIView):
    """
    API endpoint that allows to view the Pokémon added to the team, and their assigned moves.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class_Team = TeamSerializer
    serializer_class_PokemonMove = PokemonMovesSerializer

    def get_queryset_team(self, user):
        """
        This queryset should return a list of all the Pokémon in the team of the user.
        """
        return Team.objects.filter(user=user)

    def get_queryset_pokemonmove(self, user):
        """
        This queryset should return a list of all the moves of Pokémon in the team of the user.
        """
        return PokemonMoves.objects.in_team(user).filter(user=user)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        team = self.serializer_class_Team(self.get_queryset_team(user), many=True)
        move = self.serializer_class_PokemonMove(self.get_queryset_pokemonmove(user), many=True)
        data = {'Team': team.data,
                'Pokemon moves:': move.data
                }
        return Response(data)


class PokemonDetail(APIView):
    """
        API endpoint that retrieves pokemon data from the PokeAPI.
        """

    def get(self, request, pokemon_name):
        pokemon_url = urljoin(POKE_API_ENDPOINT + POKEMON, pokemon_name)
        pokemon_species_url = urljoin(POKE_API_ENDPOINT + POKEMON_SPECIES, pokemon_name)
        data = requests.get(pokemon_species_url).json()
        flavor_text = data['flavor_text_entries'][0]['flavor_text']
        pokemon_data = requests.get(pokemon_url).json()
        pokemon_id = pokemon_data['id']
        pokemon_types_list = pokemon_data['types']
        pokemon_abilities_list = pokemon_data['abilities']
        pokemon_moves_list = pokemon_data['moves']
        pokemon_img = pokemon_data['sprites']['other']['official-artwork']['front_default']
        pokemon_img_shiny = pokemon_data['sprites']['other']['official-artwork']['front_shiny']
        data = {'pokemon_name': pokemon_name,
                'pokemon_id': pokemon_id,
                'pokemon_types_list': pokemon_types_list,
                'pokemon_abilities_list': pokemon_abilities_list,
                'pokemon_moves_list': pokemon_moves_list,
                'pokemon_img': pokemon_img,
                'pokemon_img_shiny': pokemon_img_shiny,
                'pokemon_entry': flavor_text,
                }
        return Response(data)


class MovesView(TemplateView):
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


class MoveDetailView(TemplateView):
    template_name = 'pokemons/move_detail.html'

    def get(self, request, id_or_name):
        url = urljoin(POKE_API_ENDPOINT + MOVES, id_or_name)
        pokemon_move = requests.get(url).json()
        id = pokemon_move['id']
        name = pokemon_move['name']
        accuracy = pokemon_move['accuracy']
        power = pokemon_move['power']
        pp = pokemon_move['pp']
        type = pokemon_move['type']
        move_class = pokemon_move['damage_class']
        flavor_text_list = pokemon_move['flavor_text_entries']
        if request.user.is_authenticated:
            move = Move.objects.get_or_create(
                move_id=id,
                move_name=name,
                move_type=type['name'],
            )
            move = move[0]
        context = {'name': name,
                   'accuracy': accuracy,
                   'power': power,
                   'pp': pp,
                   'type': type,
                   'class': move_class,
                   'flavor_text_list': flavor_text_list,
                   }
        return render(request, self.template_name, context)


class MoveViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows all moves to be viewed.
    """
    queryset = Move.objects.all()
    serializer_class = MoveSerializer
    permission_classes = [permissions.AllowAny]


class PokemonMovesList(APIView):
    """
    API endpoint that allows to view the Pokémon and their assigned moves.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        This view should return a list of all the Pokémon and their moves, filtered by the current user.
        """
        pokemon_moves = PokemonMoves.objects.filter(user=request.user)
        serialized_pokemon_moves = PokemonMovesSerializer(pokemon_moves, many=True)
        return Response(serialized_pokemon_moves.data)


class PokemonTypeDetailView(TemplateView):
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
    template_name = 'pokemons/pokemon_types.html'

    def get_context_data(self, **kwargs):
        url = urljoin(POKE_API_ENDPOINT, TYPES)
        pokemon_types = requests.get(url).json()
        context = super().get_context_data(**kwargs)
        context['type_list'] = pokemon_types['results']
        return context
