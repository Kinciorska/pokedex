from django.views.generic.base import TemplateView
from urllib.parse import urljoin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.shortcuts import render, redirect, get_object_or_404


import requests


from pokemon_moves.models import Move, PokemonMoves
from pokemon_moves.serializers import MoveSerializer, PokemonMovesSerializer

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

    # def get_context_data(self, id_or_name, **kwargs):
    #     url = urljoin(POKE_API_ENDPOINT + MOVES, id_or_name)
    #     pokemon_move = requests.get(url).json()
    #     context = super().get_context_data(**kwargs)
    #     context['name'] = pokemon_move['name']
    #     context['accuracy'] = pokemon_move['accuracy']
    #     context['power'] = pokemon_move['power']
    #     context['pp'] = pokemon_move['pp']
    #     context['type'] = pokemon_move['type']
    #     context['class'] = pokemon_move['damage_class']
    #     context['flavor_text_list'] = pokemon_move['flavor_text_entries']
    #     return context
    #
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
    queryset = Move.objects.all()
    serializer_class = MoveSerializer
    permission_classes = [permissions.IsAuthenticated]

class PokemonMovesList(APIView):
    def get(self, request, format=None):
        user = request.user
        pokemon_moves = PokemonMoves.objects.filter(user=user)
        serializer = PokemonMovesSerializer
        return Response(serializer.data)
