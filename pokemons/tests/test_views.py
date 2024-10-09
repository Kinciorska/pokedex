from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from pokemons.models import Pokemon
from pokemons.views import PokemonView


class HomePageTestCase(TestCase):

    def test_home_page_url(self):
        response = self.client.get("/pokemons/home/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/home.html')

    def test_home_page_view_name(self):
        response = self.client.get(reverse('pokemons:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/home.html')


class PokemonViewTestCase(TestCase):

    def setUp(self) -> None:
        self.pokemon = Pokemon.objects.create(pokemon_id=1,
                                              pokemon_name='Test Pokemon',
                                              pokemon_height=10,
                                              pokemon_weight=10,
                                              pokemon_img='img_link',
                                              pokemon_img_shiny='img_shiny_link',
                                              pokemon_entry='test pokemon entry',
                                              pokemon_type_1='grass',
                                              pokemon_type_2='water'
                                              )

    def test_pokemon_page_url(self):
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/pokemon.html')

    def test_pokemon_view_name(self):
        response = self.client.get(reverse('pokemons:pokemon_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/pokemon.html')

    def test_pokemon_view_without_login(self):
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.context['is_favourite'], False)
        self.assertEqual(response.context['team_full'], False)
        self.assertEqual(response.context['moves_full'], False)
        self.assertEqual(response.context['move_names'], [])

    @patch('pokemons.views.PokemonView.save_in_team')
    def test_pokemon_view_save_in_team_called(self, mock_save_in_team):
        PokemonView.save_in_team(request=self.client.post('/pokemons/pokemon/1/'), pokemon_id=self.pokemon.pokemon_id)
        mock_save_in_team.assert_called()

    @patch('pokemons.views.PokemonView.save_in_favourites')
    def test_pokemon_view_save_in_favourites_called(self, mock_save_in_favourites):
        PokemonView.save_in_favourites(request=self.client.post('/pokemons/pokemon/1/'), pokemon_id=self.pokemon.pokemon_id)
        mock_save_in_favourites.assert_called()

    @patch('pokemons.views.PokemonView.add_move')
    def test_pokemon_view_add_move_called(self, mock_add_move):
        PokemonView.add_move(request=self.client.post('/pokemons/pokemon/1/'), pokemon_id=self.pokemon.pokemon_id)
        mock_add_move.assert_called()

    @patch('pokemons.views.PokemonView.remove_move')
    def test_pokemon_view_remove_move_called(self, mock_remove_move):
        PokemonView.remove_move(request=self.client.post('/pokemons/pokemon/1/'), pokemon_id=self.pokemon.pokemon_id)
        mock_remove_move.assert_called()
