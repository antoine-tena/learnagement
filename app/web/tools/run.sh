#!/usr/bin/env bash
# Lance une commande PHP (composer, vendor/bin/…) dans app/web/ : avec le PHP de la machine s'il est
# là, sinon dans l'image composer officielle, par podman (ou docker). Installe vendor/ au besoin.
#   app/web/tools/run.sh composer install
#   app/web/tools/run.sh vendor/bin/phpstan analyse
set -euo pipefail

readonly COMPOSER_IMAGE="docker.io/library/composer:2"
web_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$web_dir"

run() {
    if command -v php >/dev/null && command -v composer >/dev/null; then
        "$@"
        return
    fi
    local engine
    engine="$(command -v podman || command -v docker || true)"
    if [[ -z "$engine" ]]; then
        echo "Ni PHP ni podman : installez l'un des deux pour vérifier le PHP de app/web/." >&2
        return 1
    fi
    local user_options=(--user "$(id -u):$(id -g)")
    if [[ "$(basename "$engine")" == "podman" ]]; then
        user_options=(--userns=keep-id)
    fi
    "$engine" run --rm "${user_options[@]}" -v "$web_dir:/app:Z" -w /app \
        -e HOME=/tmp -e COMPOSER_CACHE_DIR=/tmp/composer-cache "$COMPOSER_IMAGE" "$@"
}

if [[ "${1:-}" == vendor/bin/* && ! -x "$1" ]]; then
    run composer install --no-interaction --no-progress
fi
run "$@"
