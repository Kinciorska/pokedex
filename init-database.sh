#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER pokedexuser WITH ENCRYPTED PASSWORD 'pokedexpassword';
    CREATE DATABASE pokedex ENCODING 'UTF8'  OWNER pokedexuser;
EOSQL