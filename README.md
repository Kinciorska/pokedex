# Pokemon Team Builder App

This Python application is designed to make possible creating Pokémon teams, as well as assigning moves to Pokémon. The user can browse, compare and customize their team according to their strategy and preferences and choose their favorite Pokémon. 

## Features

 **Pokémon Database**: Connected to a comprehensive database of Pokémon species, including their stats, types, abilities, and move sets.

 **Team Creation**: Easily create and manage your Pokémon teams. The app provides a user-friendly interface to add, remove, and organize your Pokémon members.

 **Pokémon Moveset**: Browse through the list of all available moves for a Pokémon, assign, manage and organize the moves for best performance.

## Getting Started

Follow these steps to build and run the app.

### Clone the repository:

   ```bash
   git clone https://github.com/Kinciorska/pokedex.git
   ```
### Change into the correct directory
```
cd pokedex
```

### Build the Docker Image:

Needed environment files:

- .django

- .postgres

- .rabbitmq

Environment files should be located in .envs directory, examples of these environment files are available in the same directory.

Build the Docker container using
```
docker compose build 
```

### Run the Docker Container:
Run the Docker container in the background using
```
docker compose up -d
```
### Apply migrations:
Apply Django migrations using
```
docker compose run web python manage.py migrate
```

### Start Celery:
Start the worker and the beat using
```
docker compose run web celery -A pokedex worker --beat --scheduler django --loglevel=info
```

### Save all the moves, all the Pokémon, and the possible moves for a Pokémon to the database:
Start the terminal using
```
docker compose run web python manage.py shell
```
Start the "create_all_pokemon", "create_all_moves" and "create_pokemon_moves" tasks using
```
>>> from pokemons.tasks import "task_name"
>>> "task_name()"
```

Note that the "create_pokemon_moves" task should be executed only after creating all the Pokémon and moves.

### Technologies
- Django
- DRF
- PostgreSQL
- Docker
- RabbitMQ
- Celery


#### License
This Pokémon Team Builder App is open-source and distributed under the MIT License.

##### Acknowledgements
Special thanks to PokéAPI for providing the Pokémon data used in this app.
