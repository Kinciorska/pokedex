from django.urls import path

from pokemon_moves.views import (MovesView,
                                 MoveDetailView,
                                 )

app_name = 'pokemon_moves'

urlpatterns = [
    path('', MovesView.as_view(), name="pokemon_moves"),
    path('move/<str:id_or_name>/', MoveDetailView.as_view(), name="move_details"),

]
