from pokemons.models import Pokemon, Team
from rest_framework import serializers


class PokemonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pokemon
        fields = ['pokemon_id', 'pokemon_name', 'pokemon_type_1', 'pokemon_type_2']


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        # fields = ['user', 'pokemon_id', 'pokemon_number']
        fields = ['pokemon_number']
        depth = 1

