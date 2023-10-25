from django.urls import path

from pokemons.views import (
    HomePageView,
    PokemonView,
    SearchPokemonView,
    FavouritePokemonView,
    PokemonTeamView,
    AddMoveToPokemonView
    )

app_name = 'pokemons'

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),
    path('pokemon/<id_or_name>/', PokemonView.as_view(), name='pokemon_detail'),
    path('search/', SearchPokemonView.as_view(), name='search_pokemon'),
    path('favourites/', FavouritePokemonView.as_view(), name='favourite_pokemon'),
    path('team/', PokemonTeamView.as_view(), name='pokemon_team'),
    path('add_move/<pokemon>/<str:move>/', AddMoveToPokemonView.as_view(), name='add_move'),
]
