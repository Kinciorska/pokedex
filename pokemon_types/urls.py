from django.urls import path

from pokemon_types.views import (PokemonTypeView,
                                 )

app_name = 'pokemon_types'

urlpatterns = [
    path('type/<str:id_or_name>/', PokemonTypeView.as_view(), name="pokemon_type"),
]