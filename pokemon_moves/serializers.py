from pokemon_moves.models import Move, PokemonMoves
from rest_framework import serializers


class MoveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Move
        fields = ['move_id', 'move_name', 'move_type']


class PokemonMovesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PokemonMoves
        fields = ['user', 'number', 'move', 'pokemon']
