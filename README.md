# Pokedex App

This Python application is designed to make possible creating Pokemon teams, as well as assigning moves to pokemons. The user can browse, compare and customize their team according to their strategy and preferences and choose their favorite Pokemon. 

## Features

 **Pokemon Database**: Connected to a comprehensive database of Pokemon species, including their stats, types, abilities, and move sets.

 **Team Creation**: Easily create and manage your Pokemon teams. The app provides a user-friendly interface to add, remove, and organize your Pokemon members.


## Getting Started

Follow these steps to build and run the app.

### Clone the repository:

   ```bash
   git clone https://github.com/Kinciorska/pokedex.git
   ```
### Set up the Python virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

### Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```


### Build the Docker Image:

Needed environment files:

- .django

- .postgres

- .rabbitmq

Environment files should be located in .envs directory, examples of these environment files are available in the same directory.
 
Build the Docker container using
```
docker-compose build
```
### Build the Docker Container:
Run the Docker container in the background using
```
docker-compose up -d
```
### Apply migrations:
Apply Django migrations using
```
docker-compose run web python manage.py migrate
```


### Start Celery:
Start the worker and the beat using
```
docker-compose run web celery -A pokedex worker --beat --scheduler django --loglevel=info
```

### Save all the moves, all the Pokémon, and the possible moves for a Pokémon to the database:
Start the terminal using
```
docker-compose run web python manage.py shell
```
Start the "create_all_pokemon", "create_all_moves" and "create_pokemon_moves" tasks using
```
>>> from pokemons.tasks import "task_name"
>>> "task_name()"
```

Note that the "create_pokemon_moves" task should be executed only after creating all the Pokémon and moves.

### Technologies
- Django
- PostgreSQL
- Docker
- RabbitMQ
- Celery


#### License
This Pokemon Team Builder App is open-source and distributed under the MIT License.

##### Acknowledgements
Special thanks to PokeAPI for providing the Pokemon data used in this app.
