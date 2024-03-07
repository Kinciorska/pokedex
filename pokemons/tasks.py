import requests

from celery import shared_task

# from django.core.exceptions import ObjectDoesNotExist

from django_celery_beat.models import PeriodicTask, IntervalSchedule

from urllib.parse import urljoin

from .models import Pokemon, Move
from .utils import POKE_API_ENDPOINT, POKEMON, MOVES

schedule, created = IntervalSchedule.objects.update_or_create(
    every=1,
    period=IntervalSchedule.DAYS,
)

PeriodicTask.objects.update_or_create(
    interval=schedule,
    name='Updating pokemon data',
    task='pokemons.tasks.update_all_pokemon',
)

@shared_task(name='create_all_pokemon')
def create_all_pokemon():
    pokemon_list_url = urljoin(POKE_API_ENDPOINT + POKEMON, '?limit=-1')
    pokemon_list_json = requests.get(pokemon_list_url).json()
    pokemon_list = pokemon_list_json['results']
    for pokemon in pokemon_list:
        pokemon_url = pokemon['url']
        pokemon_name = pokemon['name']
        pokemon_data = requests.get(pokemon_url).json()
        pokemon_id = pokemon_data['id']
        pokemon_weight = pokemon_data['weight']
        pokemon_height = pokemon_data['height']
        pokemon_img = pokemon_data['sprites']['other']['official-artwork']['front_default']
        pokemon_img_shiny = pokemon_data['sprites']['other']['official-artwork']['front_shiny']
        pokemon_species_url = pokemon_data['species']['url']
        data = requests.get(pokemon_species_url).json()
        flavor_texts_all = data['flavor_text_entries']
        for text in flavor_texts_all:
            if text['language']['name'] == 'en':
                flavor_text = text['flavor_text']
                break
            else:
                flavor_text = 'This pokemon is still unknown'
        pokemon_type_1 = pokemon_data['types'][0]['type']['name']
        try:
            pokemon_type_2 = pokemon_data['types'][1]['type']['name']
        except IndexError:
            pokemon_type_2 = ''

        if Pokemon(pokemon_type_1=pokemon_type_1, pokemon_type_2=pokemon_type_2).clean():
            Pokemon.objects.create(
                pokemon_id=pokemon_id,
                pokemon_name=pokemon_name,
                pokemon_height=pokemon_height,
                pokemon_weight=pokemon_weight,
                pokemon_img=pokemon_img,
                pokemon_img_shiny=pokemon_img_shiny,
                pokemon_type_1=pokemon_type_1,
                pokemon_type_2=pokemon_type_2,
                pokemon_entry=flavor_text)


@shared_task(name='update_all_pokemon')
def update_all_pokemon():
    pokemon_list_url = urljoin(POKE_API_ENDPOINT + POKEMON, '?limit=-1')
    pokemon_list_json = requests.get(pokemon_list_url).json()
    pokemon_list = pokemon_list_json['results']
    for pokemon in pokemon_list:
        pokemon_url = pokemon['url']
        pokemon_name = pokemon['name']
        pokemon_data = requests.get(pokemon_url).json()
        pokemon_id = pokemon_data['id']
        pokemon_weight = pokemon_data['weight']
        pokemon_height = pokemon_data['height']
        pokemon_img = pokemon_data['sprites']['other']['official-artwork']['front_default']
        pokemon_img_shiny = pokemon_data['sprites']['other']['official-artwork']['front_shiny']
        pokemon_species_url = pokemon_data['species']['url']
        data = requests.get(pokemon_species_url).json()
        flavor_texts_all = data['flavor_text_entries']
        for text in flavor_texts_all:
            if text['language']['name'] == 'en':
                flavor_text = text['flavor_text']
                break
            else:
                flavor_text = 'This pokemon is still unknown'
        pokemon_type_1 = pokemon_data['types'][0]['type']['name']
        try:
            pokemon_type_2 = pokemon_data['types'][1]['type']['name']
        except IndexError:
            pokemon_type_2 = ''

        pokemon, created = Pokemon.objects.update_or_create(
            pokemon_id=pokemon_id,
            defaults={
                'pokemon_name': pokemon_name,
                'pokemon_type_1': pokemon_type_1,
                'pokemon_type_2': pokemon_type_2,
                'pokemon_height': pokemon_height,
                'pokemon_weight': pokemon_weight,
                'pokemon_img': pokemon_img,
                'pokemon_img_shiny': pokemon_img_shiny,
                'pokemon_entry': flavor_text,
            }
        )


@shared_task(name='create_all_moves')
def create_all_moves():
    moves_list_url = urljoin(POKE_API_ENDPOINT + MOVES, '?limit=-1')
    moves_list_json = requests.get(moves_list_url).json()
    moves_list = moves_list_json['results']
    for move in moves_list:
        move_url = move['url']
        move_name = move['name']
        move_data = requests.get(move_url).json()
        move_id = move_data['id']
        move_type = move_data['type']['name']
        move_accuracy = move_data['accuracy']
        move_pp = move_data['pp']
        move_priority = move_data['priority']
        move_power = move_data['power']
        move_damage_class = move_data['damage_class']['name']
        flavor_texts_all = move_data['flavor_text_entries']
        for text in flavor_texts_all:
            if text['language']['name'] == 'en':
                flavor_text = text['flavor_text']
                break
            else:
                flavor_text = 'This move is still unknown'

        Move.objects.create(
            move_id=move_id,
            move_name=move_name,
            move_type=move_type,
            move_accuracy=move_accuracy,
            move_pp=move_pp,
            move_priority=move_priority,
            move_power=move_power,
            move_damage_class=move_damage_class,
            move_entry=flavor_text
        )


@shared_task(name='update_all_moves')
def update_all_moves():
    moves_list_url = urljoin(POKE_API_ENDPOINT + MOVES, '?limit=-1')
    moves_list_json = requests.get(moves_list_url).json()
    moves_list = moves_list_json['results']
    for move in moves_list:
        move_url = move['url']
        move_name = move['name']
        move_data = requests.get(move_url).json()
        move_id = move_data['id']
        move_type = move_data['type']['name']
        move_accuracy = move_data['accuracy']
        move_pp = move_data['pp']
        move_priority = move_data['priority']
        move_power = move_data['power']
        move_damage_class = move_data['damage_class']['name']
        flavor_texts_all = move_data['flavor_text_entries']
        for text in flavor_texts_all:
            if text['language']['name'] == 'en':
                flavor_text = text['flavor_text']
                break
            else:
                flavor_text = 'This move is still unknown'

        move, created = Move.objects.update_or_create(
            move_id=move_id,
            defaults={
                'move_name': move_name,
                'move_type': move_type,
                'move_accuracy': move_accuracy,
                'move_pp': move_pp,
                'move_priority': move_priority,
                'move_power': move_power,
                'move_damage_class': move_damage_class,
                'move_entry': flavor_text,
            }
        )
