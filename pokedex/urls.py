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
from rest_framework import routers

from website.views import HomePageView, RegisterView, LoginView, LogoutView, UserViewSet, GroupViewSet
from pokemon_moves.views import MoveViewSet
from pokemons.views import PokemonViewSet, TeamViewSet, FavouritePokemonViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'moves', MoveViewSet)
router.register(r'pokemon', PokemonViewSet, basename='pokemon')
router.register(r'team', TeamViewSet, basename='team')
router.register(r'favourite', FavouritePokemonViewSet, basename='favourite')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', HomePageView.as_view(), name="home"),
    path('register', RegisterView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('', include(router.urls)),
    path('-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('pokemons/', include('pokemons.urls')),
    path('types/', include('pokemon_types.urls')),
    path('pokemon_moves/', include('pokemon_moves.urls')),
]
