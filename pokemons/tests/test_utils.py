import requests
import requests_mock

from django.test import TestCase

import pokemons.utils


class UtilsTestCase(TestCase):

    def setUp(self):
        self.data = {
            'type': {
                'name': 'normal',
                'url': 'https://pokeapi.co/api/v2/type/1/'
            },
            'id': 1,
        }

    @requests_mock.Mocker()
    def test_get_pokemon_id(self, m):
        m.register_uri('GET', 'http://test.com', json=self.data, status_code=200)
        pokemon = requests.get('http://test.com').json()
        pokemon_id = pokemon['id']
        self.assertEqual(pokemon_id, 1)

    @requests_mock.Mocker()
    def test_get_move_details(self, m):
        m.register_uri('GET', 'http://test.com', json=self.data, status_code=200)
        move = requests.get('http://test.com').json()
        move_id = move['id']
        move_type = move['type']['name']
        self.assertEqual(move_id, 1)
        self.assertEqual(move_type, 'normal')

    def test_get_missing_number(self):
        missing_number = pokemons.utils.get_missing_number(numbers={1, 2, 3, 4}, existing_numbers=[1, 3])
        self.assertEqual(missing_number, 2)
