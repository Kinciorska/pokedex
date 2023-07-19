from django.urls import path

from pokemon_moves.views import (PokemonMovesView,
                                 PokemonMoveDetailView,
                                 )

app_name = 'pokemon_moves'

urlpatterns = [
    path('', PokemonMovesView.as_view(), name="pokemon_moves"),
    path('move/<str:id_or_name>/', PokemonMoveDetailView.as_view(), name="move_details"),

]
