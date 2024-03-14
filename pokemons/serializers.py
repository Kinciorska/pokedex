from rest_framework import serializers

from .models import Pokemon, Team, FavouritePokemon, Move, UserPokemonMoves


class PokemonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['pokemon_id', 'pokemon_name', 'pokemon_type_1', 'pokemon_type_2']


class PokemonIdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['pokemon_id']


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    pokemon_id = PokemonIdSerializer(read_only=True, many=True)

    class Meta:
        model = Team
        fields = ['pokemon_number', 'pokemon_id']
        depth = 1


class MoveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Move
        fields = ['move_id', 'move_name', 'move_type']


class UserPokemonMovesSerializer(serializers.HyperlinkedModelSerializer):
    pokemon = PokemonSerializer(read_only=True, many=False)
    move = MoveSerializer(read_only=True, many=False)

    class Meta:
        model = UserPokemonMoves
        fields = ['pokemon', 'move_number', 'move']
        depth = 1


class FavouritePokemonSerializer(serializers.HyperlinkedModelSerializer):
    pokemon = PokemonSerializer(many=False)

    class Meta:
        model = FavouritePokemon
        fields = ['pokemon']
        depth = 1
