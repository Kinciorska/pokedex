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
    """Returns the id of the Pokémon fetched from the PokéAPI."""

    url = urljoin(POKE_API_ENDPOINT + POKEMON, id_or_name)
    pokemon = requests.get(url).json()
    pokemon_id = pokemon['id']
    return pokemon_id

def get_move_details(move_name):
    """Returns the move id and type fetched from the PokéAPI."""

    url = urljoin(POKE_API_ENDPOINT + MOVES, move_name)

    try:
        move = requests.get(url).json()
        id = move['id']
        type = move['type']['name']
        return id, type

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch move data from {url}: {e}")
        return None, None

def get_missing_number(numbers, existing_numbers):
    """Returns the first missing number from a set of numbers."""

    missing_number = list(numbers - set(existing_numbers))[0]
    return missing_number
