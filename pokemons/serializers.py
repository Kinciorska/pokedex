from pokemons.models import Pokemon, Team, FavouritePokemon
from pokemon_moves.serializers import MoveSerializer
from pokemon_moves.models import PokemonMoves

from rest_framework import serializers


class PokemonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['pokemon_id', 'pokemon_name', 'pokemon_type_1', 'pokemon_type_2']

class PokemonIdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['pokemon_id']


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    pokemon_id = PokemonSerializer(read_only=True, many=True)
    class Meta:
        model = Team
        fields = ['pokemon_number', 'pokemon_id']
        depth = 1

class PokemonMovesSerializer(serializers.HyperlinkedModelSerializer):
    pokemon = PokemonIdSerializer(read_only=True, many=False)
    move = MoveSerializer(read_only=True, many=False)

    class Meta:
        model = PokemonMoves
        fields = ['pokemon', 'move_number', 'move']
        depth = 1



class FavouritePokemonSerializer(serializers.HyperlinkedModelSerializer):
    pokemon = PokemonSerializer(many=False)
    class Meta:
        model = FavouritePokemon
        fields = ['pokemon']
        depth = 1
