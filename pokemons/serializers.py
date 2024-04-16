from rest_framework import serializers

from .models import Pokemon, Team, FavouritePokemon, Move, UserPokemonMoves


class PokemonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['pokemon_id', 'pokemon_name', 'pokemon_type_1', 'pokemon_type_2']


class MoveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Move
        fields = ['move_id', 'move_name', 'move_type']


class UserPokemonMovesSerializer(serializers.HyperlinkedModelSerializer):
    move = MoveSerializer(read_only=True, many=False)

    class Meta:
        model = UserPokemonMoves
        fields = ['move_number', 'move']
        depth = 1

class PokemonMovesSerializer(serializers.HyperlinkedModelSerializer):
    user_moves = UserPokemonMovesSerializer(read_only=True, many=True)

    class Meta:
        model = Pokemon
        fields = ['pokemon_id', 'pokemon_name', 'pokemon_type_1', 'pokemon_type_2', 'user_moves']
        depth = 1

class FavouritePokemonSerializer(serializers.HyperlinkedModelSerializer):
    pokemon = PokemonMovesSerializer(many=False)

    class Meta:
        model = FavouritePokemon
        fields = ['pokemon']
        depth = 1


class UserTeamPokemonMovesSerializer(serializers.HyperlinkedModelSerializer):
    move = MoveSerializer(read_only=True, many=False)

    class Meta:
        model = UserPokemonMoves
        fields = ['move_number', 'move']

class PokemonInTeamSerializer(serializers.HyperlinkedModelSerializer):
    user_moves = UserTeamPokemonMovesSerializer(read_only=True, many=True)

    class Meta:
        model = Pokemon
        fields = ['pokemon_id', 'pokemon_name', 'pokemon_type_1', 'pokemon_type_2', 'user_moves']
        depth = 1


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    pokemon = PokemonInTeamSerializer(read_only=True, many=True)

    class Meta:
        model = Team
        fields = ['pokemon_number', 'pokemon']
        depth = 1

