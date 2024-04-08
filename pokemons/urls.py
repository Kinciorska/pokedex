from django.urls import path

from pokemons.views import (
    HomePageView,
    PokemonView,
    SearchPokemonView,
    FavouritePokemonView,
    PokemonTeamView,
    MovesView,
    MoveDetailView,
    PokemonTypesView,
    PokemonTypeDetailView,
)

app_name = 'pokemons'

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('pokemon/<id_or_name>/', PokemonView.as_view(), name='pokemon_detail'),
    path('search/', SearchPokemonView.as_view(), name='search_pokemon'),
    path('favourites/', FavouritePokemonView.as_view(), name='favourite_pokemon'),
    path('team/', PokemonTeamView.as_view(), name='pokemon_team'),
    path('moves', MovesView.as_view(), name="pokemon_moves"),
    path('move/<str:id_or_name>/', MoveDetailView.as_view(), name="move_detail"),
    path('pokemon_types', PokemonTypesView.as_view(), name="pokemon_types"),
    path('type/<str:id_or_name>/', PokemonTypeDetailView.as_view(), name="type_detail"),
]
