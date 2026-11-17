#!/bin/sh

set -e

echo "PHP container starting..."

cd /var/www/html

# Les dépendances aux versions de composer.lock, jamais mises à jour au démarrage. En production,
# sans les outils de vérification (require-dev) ; ailleurs, vendor/ est partagé avec la machine
# du développeur, qui s'en sert pour vérifier le PHP (web/tools/run.sh).
if [ -f composer.json ] ; then
    echo "Installing Composer dependencies..."
    if [ "$ENV" = "prod" ]; then
        composer install --no-interaction --no-dev --optimize-autoloader
    else
        composer install --no-interaction
    fi
fi

# Activer le vhost SSL uniquement en production
if [ -f .env ]; then
    INSTANCE_NAME=$(grep -E '^INSTANCE_NAME=' .env | cut -d '=' -f2 | tr -d '\r')
fi

if [ "$ENV" = "prod" ]; then
    echo "Production détectée — activation du vhost SSL..."
    a2enmod ssl
    a2ensite ssl.conf
else
    echo "Environnement non-prod ($INSTANCE_NAME) — SSL vhost ignoré."
fi

echo "Starting Apache..."
exec apache2-foreground
