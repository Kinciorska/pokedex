from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from pokemons.models import Team, FavouritePokemon, UserPokemonMoves
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

    def test_pokemon_view_saved_pokemon_in_team(self):
        self.client.post(reverse('login'), data=self.form_data)
        self.client.post('/pokemons/pokemon/1/',
                         id_or_name=1,
                         data={'csrfmiddlewaretoken': ['test'],
                               'is_added': ['on'],
                               'team_form': ['Add to team']})
        check_added_pokemon_to_team = Team.objects.filter(user=self.user,
                                                          pokemon_number=1).exists()
        self.assertTrue(check_added_pokemon_to_team)

    def test_pokemon_view_saved_pokemon_in_favourites(self):
        self.client.post(reverse('login'), data=self.form_data)
        self.client.post('/pokemons/pokemon/1/',
                         id_or_name=1,
                         data={'csrfmiddlewaretoken': ['test'],
                               'is_added': ['on'],
                               'favourite_form': ['Add to favourites']})
        check_added_pokemon_to_favourites = FavouritePokemon.objects.filter(user=self.user,
                                                                            pokemon=self.pokemon).exists()
        self.assertTrue(check_added_pokemon_to_favourites)

    def test_pokemon_view_move_added(self):
        self.client.post(reverse('login'), data=self.form_data)
        self.client.post('/pokemons/pokemon/1/',
                         id_or_name=1,
                         data={'csrfmiddlewaretoken': ['test'],
                               'move_name': ['cut'],
                               'add_move_form': ['Choose this move']})
        check_move_added = UserPokemonMoves.objects.filter(user=self.user,
                                                           pokemon=self.pokemon,
                                                           move_number=1).exists()
        self.assertTrue(check_move_added)

    def test_pokemon_view_move_removed(self):
        self.client.post(reverse('login'), data=self.form_data)
        move = baker.make('pokemons.Move',
                          move_name='cut')
        baker.make('pokemons.UserPokemonMoves',
                   user=self.user,
                   pokemon=self.pokemon,
                   move=move)
        self.client.post('/pokemons/pokemon/1/',
                         id_or_name=1,
                         data={'csrfmiddlewaretoken': ['test'],
                               'move_name': ['cut'],
                               'remove_move_form': ['Remove this move']})
        check_move_removed = UserPokemonMoves.objects.filter(user=self.user,
                                                             pokemon=self.pokemon,
                                                             move=move).exists()
        self.assertFalse(check_move_removed)


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
        self.client.post('/pokemons/team/', data={'csrfmiddlewaretoken': ['test'],
                                                  'pokemon_number': ['1'],
                                                  'team_form': ['Remove from team']})
        check_deleted_pokemon_in_team = Team.objects.filter(user=self.user,
                                                            pokemon_number=1).exists()
        self.assertFalse(check_deleted_pokemon_in_team)


class SearchPokemonViewTestCase(TestCase):

    def setUp(self) -> None:
        self.pokemon = baker.make('pokemons.Pokemon',
                                  pokemon_id=1)

    def test_search_page_url(self):
        response = self.client.get('/pokemons/search/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/search.html')

    def test_search_page_view_name(self):
        response = self.client.get(reverse('pokemons:search_pokemon'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/search.html')

    def test_valid_pokemon_search(self):
        response = self.client.post(reverse('pokemons:search_pokemon'), data={'id_or_name': 1})
        self.assertRedirects(response,
                             '/pokemons/pokemon/1/',
                             status_code=302,
                             target_status_code=200)

    def test_invalid_pokemon_search(self):
        response = self.client.post(reverse('pokemons:search_pokemon'), data={'id_or_name': 'invalid_data'}, follow=True)
        self.assertRedirects(response,
                             '/pokemons/home/',
                             status_code=302,
                             target_status_code=200)


class FavouritePokemonViewTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@email.com',
                                             password='FQ8fgxesdzUz')
        self.client.post(reverse('login'), data={'username': 'testuser',
                                                 'password': 'FQ8fgxesdzUz'})

    def test_favourite_pokemon_page_url(self):
        response = self.client.get('/pokemons/favourites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/favourite_pokemon.html')

    def test_favourite_pokemon_page_view_name(self):
        response = self.client.get(reverse('pokemons:favourite_pokemon'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='pokemons/favourite_pokemon.html')

    def test_remove_favourite_pokemon(self):
        pokemon = baker.make('pokemons.Pokemon',
                             pokemon_id=1)
        baker.make('pokemons.FavouritePokemon',
                   user=self.user,
                   pokemon=pokemon)
        response = self.client.post(reverse('pokemons:favourite_pokemon'), data={'pokemon_id': 1})
        self.assertEqual(response.status_code, 302)
        check_pokemon_in_favourites = FavouritePokemon.objects.filter(user=self.user,
                                                                      pokemon=pokemon).exists()
        self.assertFalse(check_pokemon_in_favourites)
