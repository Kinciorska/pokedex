from django.urls import path

from pokemons.views import (
    HomePageView,
    PokemonView,
    SearchPokemonView,
    FavouritePokemonView,
    AddFavouritePokemonView,
    RemoveFavouritePokemonView,
    PokemonTeamView,
    AddPokemonToTeamView,
    RemovePokemonFromTeamView,
    )

app_name = 'pokemons'

urlpatterns = [
    path('home/', HomePageView.as_view(), name="home"),
    path('pokemon/<str:id_or_name>/', PokemonView.as_view(), name="pokemon_detail"),
    path('search/', SearchPokemonView.as_view(), name="search_pokemon"),
    path('favourites/', FavouritePokemonView.as_view(), name="favourite_pokemon"),
    path('add_favourite/<id_or_name>/', AddFavouritePokemonView.as_view(), name="add_fav_pokemon"),
    path('remove_favourite/<id_or_name>/', RemoveFavouritePokemonView.as_view(), name="remove_fav_pokemon"),
    path('add_to_team/<id_or_name>/', AddPokemonToTeamView.as_view(), name="add_to_team"),
    path('remove_from_team/<id_or_name>/', RemovePokemonFromTeamView.as_view(), name="remove_from_team"),
    path('team/', PokemonTeamView.as_view(), name="pokemon_team"),
]
