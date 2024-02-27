import requests

from celery import shared_task

from django_celery_beat.models import PeriodicTask, IntervalSchedule

from urllib.parse import urljoin

from .models import Pokemon
from .utils import POKE_API_ENDPOINT, POKEMON

schedule, created = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.DAYS,
)

PeriodicTask.objects.update_or_create(
    interval=schedule,
    name='Updating pokemon data',
    task='pokemons.tasks.update_all_pokemon',
)

@shared_task
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


@shared_task
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

        pokemon = Pokemon.objects.get(pokemon_id=pokemon_id)
        pokemon.pokemon_name = pokemon_name
        pokemon.pokemon_height = pokemon_height
        pokemon.pokemon_weight = pokemon_weight
        pokemon.pokemon_img = pokemon_img
        pokemon.pokemon_img_shiny = pokemon_img_shiny
        pokemon.pokemon_type_1 = pokemon_type_1
        pokemon.pokemon_type_2 = pokemon_type_2
        pokemon.pokemon_entry = flavor_text
        pokemon.save()
