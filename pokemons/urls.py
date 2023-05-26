from django.urls import path

from pokemons.views import PokemonView

app_name = "pokemons"
urlpatterns = [
    path('<id_or_name>/', PokemonView.as_view(), name="pokemon_detail"),
]
