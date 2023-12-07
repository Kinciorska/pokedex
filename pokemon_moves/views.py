from django.views.generic.base import TemplateView
from urllib.parse import urljoin
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from django.shortcuts import render, redirect, get_object_or_404


import requests


from pokemon_moves.models import Move, PokemonMoves
from pokemons.models import Team
from pokemon_moves.serializers import MoveSerializer
from pokemons.serializers import PokemonMovesSerializer, TeamSerializer

from pokemons.utils import POKE_API_ENDPOINT, MOVES


class MovesView(TemplateView):
    template_name = 'pokemon_moves/pokemon_moves.html'

    def get_context_data(self, **kwargs):
        url = urljoin(POKE_API_ENDPOINT, MOVES)
        pokemon_moves = requests.get(url).json()
        context = super().get_context_data(**kwargs)
        context['moves_list'] = pokemon_moves['results']
        return context


class MoveDetailView(TemplateView):
    template_name = 'pokemon_moves/move_detail.html'

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
                   'accuracy':accuracy,
                   'power':power,
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


class PokemonMoveViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows moves which are assigned to Pokémon to be viewed.
    """
    queryset = Move.objects.all()
    serializer_class = MoveSerializer
    permission_classes = [permissions.AllowAny]

class PokemonMovesList(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        user = request.user
        pokemon_moves = PokemonMoves.objects.filter(user=user)
        serialized_pokemon_moves = PokemonMovesSerializer(pokemon_moves, many=True)
        return Response(serialized_pokemon_moves.data)

