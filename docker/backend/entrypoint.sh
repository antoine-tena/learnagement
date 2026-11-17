#!/bin/sh
# Be careful don't use bash and bash command

cd /app

apt-get update && apt-get install -y \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev

# L'environnement reste à côté du code monté, distinct du .venv de la machine hôte
UV_PROJECT_ENVIRONMENT=docker_venv uv sync --frozen

. docker_venv/bin/activate

if [ "$ENV" = "prod" ]; then
    # Following command must be run only if prod env ans main branch
    # pytest  || { echo "Tests échoués — arrêt du démarrage."; exit 1; }
    pytest  || { echo "Tests échoués";}
else
    pytest  || { echo "Tests échoués";}
fi

python app.py
