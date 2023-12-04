from pokemons.models import Pokemon, Team
from rest_framework import serializers


class PokemonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['pokemon_id', 'pokemon_name', 'pokemon_type_1', 'pokemon_type_2']


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    pokemon_id = PokemonSerializer(read_only=True, many=True)
    class Meta:
        model = Team
        fields = ['pokemon_number', 'pokemon_id']
        depth = 1

