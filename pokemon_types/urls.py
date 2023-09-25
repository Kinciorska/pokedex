from django.urls import path

from pokemon_types.views import (PokemonTypeDetailView,
                                PokemonTypesView,
                                 )

app_name = 'pokemon_types'

urlpatterns = [
    path('', PokemonTypesView.as_view(), name="pokemon_types"),
    path('type/<str:id_or_name>/', PokemonTypeDetailView.as_view(), name="pokemon_type"),
]