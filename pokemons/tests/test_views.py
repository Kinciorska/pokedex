from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from unittest.mock import patch

from pokemons.models import Team
from pokemons.views import PokemonView
from pokemons.utils import get_missing_number


class HomePageTestCase(TestCase):

    def test_home_page_url(self):
        response = self.client.get('/pokemons/home/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/home.html')

    def test_home_page_view_name(self):
        response = self.client.get(reverse('pokemons:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/home.html')


class PokemonViewTestCase(TestCase):

    def setUp(self) -> None:
        self.pokemon = baker.make('pokemons.Pokemon',
                                  pokemon_id=1)
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@email.com',
                                             password='FQ8fgxesdzUz')
        self.form_data = {'username': 'testuser',
                          'password': 'FQ8fgxesdzUz'}

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

    def test_pokemon_view_with_login_set_is_favourite(self):
        self.client.post(reverse('login'), data=self.form_data)
        baker.make('pokemons.FavouritePokemon',
                   pokemon=self.pokemon,
                   user=self.user)
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.context['is_favourite'], True)

    def test_pokemon_view_with_login_not_set_is_favourite(self):
        self.client.post(reverse('login'), data=self.form_data)
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.context['is_favourite'], False)

    def test_pokemon_view_with_login_set_team_full(self):
        self.client.post(reverse('login'), data=self.form_data)
        baker.make('pokemons.Team',
                   6,
                   user=self.user)
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.context['team_full'], True)

    def test_pokemon_view_with_login_not_set_team_full(self):
        self.client.post(reverse('login'), data=self.form_data)
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.context['team_full'], False)

    def test_pokemon_view_with_login_set_moves_full(self):
        self.client.post(reverse('login'), data=self.form_data)
        baker.make('pokemons.UserPokemonMoves',
                   4,
                   user=self.user,
                   pokemon=self.pokemon,
                   make_m2m=True)
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.context['moves_full'], True)

    def test_pokemon_view_with_login_not_set_moves_full(self):
        self.client.post(reverse('login'), data=self.form_data)
        response = self.client.get('/pokemons/pokemon/1/')
        self.assertEqual(response.context['moves_full'], False)

    @patch('pokemons.views.PokemonView.save_in_team')
    def test_pokemon_view_save_in_team_called(self, mock_save_in_team):
        PokemonView.save_in_team(request=self.client.post('/pokemons/pokemon/1/'), pokemon_id=self.pokemon.pokemon_id)
        mock_save_in_team.assert_called()

    @patch('pokemons.views.PokemonView.save_in_favourites')
    def test_pokemon_view_save_in_favourites_called(self, mock_save_in_favourites):
        PokemonView.save_in_favourites(request=self.client.post('/pokemons/pokemon/1/'),
                                       pokemon_id=self.pokemon.pokemon_id)
        mock_save_in_favourites.assert_called()

    @patch('pokemons.views.PokemonView.add_move')
    def test_pokemon_view_add_move_called(self, mock_add_move):
        PokemonView.add_move(request=self.client.post('/pokemons/pokemon/1/'), pokemon_id=self.pokemon.pokemon_id)
        mock_add_move.assert_called()

    @patch('pokemons.views.PokemonView.remove_move')
    def test_pokemon_view_remove_move_called(self, mock_remove_move):
        PokemonView.remove_move(request=self.client.post('/pokemons/pokemon/1/'), pokemon_id=self.pokemon.pokemon_id)
        mock_remove_move.assert_called()


class SaveInTeamTestCase(TestCase):

    def setUp(self) -> None:
        self.existing_numbers = []

    def test_calculate_missing_team_number_no_existing_number(self):
        missing_number = get_missing_number(set(range(1, 7)), self.existing_numbers)
        self.assertEqual(missing_number, 1)

    def test_calculate_missing_team_number_multiple_existing_numbers(self):
        self.existing_numbers = [1, 3]
        missing_number = get_missing_number(set(range(1, 7)), self.existing_numbers)
        self.assertEqual(missing_number, 2)


class AddMoveTestCase(TestCase):

    def setUp(self) -> None:
        self.existing_numbers = []

    def test_calculate_missing_move_number_no_existing_number(self):
        missing_number = get_missing_number(set(range(1, 5)), self.existing_numbers)
        self.assertEqual(missing_number, 1)

    def test_calculate_missing_move_number_multiple_existing_numbers(self):
        self.existing_numbers = [1, 3, 4]
        missing_number = get_missing_number(set(range(1, 5)), self.existing_numbers)
        self.assertEqual(missing_number, 2)


class PokemonTeamViewTestCase(TestCase):

    def setUp(self) -> None:
        self.pokemon = baker.make('pokemons.Pokemon',
                                  _quantity=1,
                                  pokemon_type_1='grass',
                                  pokemon_type_2='')
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@email.com',
                                             password='FQ8fgxesdzUz')
        self.team = baker.make('pokemons.Team',
                               pokemon=self.pokemon,
                               user=self.user,
                               pokemon_number=1,
                               make_m2m=True)
        self.client.post(reverse('login'), data={'username': 'testuser',
                                                 'password': 'FQ8fgxesdzUz'})

    def test_team_page_url(self):
        response = self.client.get('/pokemons/team/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/pokemon_team.html')

    def test_team_view_name(self):
        response = self.client.get(reverse('pokemons:pokemon_team'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/pokemon_team.html')

    def test_team_redirect_non_authenticated(self):
        self.client.get(reverse('logout'))
        response = self.client.get(reverse('pokemons:pokemon_team'))
        self.assertRedirects(response,
                             '/login/?next=/pokemons/team/',
                             status_code=302,
                             target_status_code=200)

    def test_pokemon_deleted_from_team(self):
        self.client.post('/pokemons/team/', data={'csrfmiddlewaretoken': ['6MH79z7z6ikjc1ZOet6dbyvXnK10QaXA5Bos8QmJQ5mv6H1CstUKeKEy2dxmJTLT'],
                                                             'pokemon_number': ['1'],
                                                             'team_form': ['Remove from team']})
        check_deleted_pokemon_in_team = Team.objects.filter(user=self.user,
                                                  pokemon_number=1).exists()
        self.assertFalse(check_deleted_pokemon_in_team)
