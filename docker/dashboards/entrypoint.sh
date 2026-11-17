#!/bin/sh
# Be careful don't use bash and bash command

cd /app

# L'environnement reste dans le conteneur, hors du code monté depuis la machine hôte ;
# uv sync le remet à jour quand uv.lock change
UV_PROJECT_ENVIRONMENT=/opt/docker_venv uv sync --frozen

. /opt/docker_venv/bin/activate

python main.py
