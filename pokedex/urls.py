"""
URL configuration for pokedex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from pokemons.views import SearchPokemonView, AddFavouritePokemon, RemoveFavouritePokemon, FavouritePokemonView
from website.views import HomePageView, RegisterView, LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name="home"),
    path('register', RegisterView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('search/', SearchPokemonView.as_view(), name="search_pokemon"),
    path('add_favourite/<id_or_name>/', AddFavouritePokemon.as_view(), name="add_fav_pokemon"),
    path('remove_favourite/<id_or_name>/', RemoveFavouritePokemon.as_view(), name="remove_fav_pokemon"),
    path('favourites/', FavouritePokemonView.as_view(), name="favourite_pokemon"),
    path('pokemons/', include('pokemons.urls')),
]
