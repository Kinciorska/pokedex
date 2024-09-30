import requests

from urllib.parse import urljoin

POKE_API_ENDPOINT = 'https://pokeapi.co/api/v2/'
POKEMON = 'pokemon/'
TYPES = 'type/'
MOVES = 'move/'
POKEMON_SPECIES = 'pokemon-species/'
TYPE_CHOICES = [('grass', 'GRASS'), ('fire', 'FIRE'), ('water', 'WATER'), ('bug', 'BUG'),
                ('normal', 'NORMAL'),
                ('poison', 'POISON'), ('electric', 'ELECTRIC'), ('ground', 'GROUND'),
                ('fighting', 'FIGHTING'),
                ('psychic', 'PSYCHIC'), ('rock', 'ROCK'), ('ghost', 'GHOST'), ('ice', 'ICE'),
                ('dragon', 'DRAGON'),
                ('dark', 'DARK'), ('steel', 'STEEL'), ('flying', 'FLYING'), ('', None)]


def get_pokemon_id(id_or_name):
    url = urljoin(POKE_API_ENDPOINT + POKEMON, id_or_name)
    pokemon = requests.get(url).json()
    pokemon_id = pokemon['id']
    return pokemon_id


def get_move_details(move_name):
    url = urljoin(POKE_API_ENDPOINT + MOVES, move_name)
    move = requests.get(url).json()
    id = move['id']
    type = move['type']['name']
    return id, type
