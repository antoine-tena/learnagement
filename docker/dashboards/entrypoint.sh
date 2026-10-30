#!/bin/sh
# Be careful don't use bash and bash command

apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

cd /app

# L'environnement reste à côté du code monté, distinct du .venv de la machine hôte
UV_PROJECT_ENVIRONMENT=docker_venv uv sync --frozen

. docker_venv/bin/activate

python main.py
