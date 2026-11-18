#!/usr/bin/env bash
# Le rapport d'une pull request, en Markdown : règles, tests, routes cassées, migrations, nouvelles
# dépendances. Chaque partie dit son verdict ; le script ne s'arrête jamais sur un échec.
#   .github/scripts/pr-report.sh <commit de base> <rapport.md>
set -uo pipefail

readonly BASE="$1"
readonly REPORT="$2"
readonly LOG_DIR="${RUNNER_TEMP:-/tmp}/pr-report"
readonly OASDIFF_IMAGE="docker.io/tufin/oasdiff:v1.39.0"
mkdir -p "$LOG_DIR"

verdict() { # verdict <code de sortie> <texte si succès> <texte si échec>
    if [[ "$1" -eq 0 ]]; then echo "✅ $2"; else echo "❌ $3"; fi
}

details() { # details <titre> <fichier> : les 60 dernières lignes, repliées
    [[ -s "$2" ]] || return 0
    printf '\n<details><summary>%s</summary>\n\n```\n' "$1"
    tail -n 60 "$2"
    printf '```\n</details>\n'
}

rules_section() {
    echo "### Règles"
    pre-commit run --color=never --from-ref "$BASE" --to-ref HEAD \
        >"$LOG_DIR/rules.log" 2>&1
    local status=$?
    verdict "$status" "Les hooks du pré-commit et la charte passent sur les fichiers changés." \
        "Des règles ne passent pas : lancez \`pre-commit run --from-ref origin/<base> --to-ref HEAD\`."
    grep -v -E 'Passed|Skipped' "$LOG_DIR/rules.log" >"$LOG_DIR/rules-failed.log"
    [[ "$status" -eq 0 ]] || details "Hooks en échec" "$LOG_DIR/rules-failed.log"
}

tests_section() {
    echo "### Tests"
    (cd app/api && uv run pytest -q --no-header -p no:cacheprovider) >"$LOG_DIR/tests.log" 2>&1
    local status=$?
    verdict "$status" "Tests de l'API : $(tail -n 1 "$LOG_DIR/tests.log")" \
        "Tests de l'API : $(tail -n 1 "$LOG_DIR/tests.log")"
    [[ "$status" -eq 0 ]] || details "Sortie de pytest" "$LOG_DIR/tests.log"
}

routes_section() {
    echo "### Routes de l'API"
    # La base peut précéder le déplacement du schéma dans app/api/.
    if ! git show "$BASE:app/api/openapi.json" >"$LOG_DIR/openapi-base.json" 2>/dev/null \
        && ! git show "$BASE:openapi.json" >"$LOG_DIR/openapi-base.json" 2>/dev/null; then
        echo "➖ Pas d'openapi.json sur la branche de base : rien à comparer."
        return
    fi
    (cd app/api && uv run python -m tools.export_openapi --output "$LOG_DIR/openapi-head.json") \
        >/dev/null 2>"$LOG_DIR/export.log"
    podman run --rm --quiet -v "$LOG_DIR:/specs:Z" "$OASDIFF_IMAGE" breaking \
        /specs/openapi-base.json /specs/openapi-head.json --fail-on ERR >"$LOG_DIR/routes.log" 2>&1
    local status=$?
    verdict "$status" "Aucune route cassée." \
        "Des routes cassées : une route publiée ne change pas, elle ouvre une nouvelle version."
    details "Changements de l'API" "$LOG_DIR/routes.log"
}

migrations_section() {
    echo "### Migrations"
    local migrations
    migrations="$(git diff --name-only --diff-filter=AM "$BASE"...HEAD -- 'database/migrations/V*.sql')"
    if [[ -z "$migrations" ]]; then
        echo "➖ Aucune migration."
        return
    fi
    echo "⚠️ Migrations à relire (jamais modifiées une fois mergées) :"
    sed 's/^/- `/; s/$/`/' <<<"$migrations"
}

dependencies_section() {
    echo "### Nouvelles dépendances"
    if ! python3 .github/scripts/new_dependencies.py "$BASE" >"$LOG_DIR/dependencies.md" 2>&1; then
        echo "❌ Les manifestes n'ont pas pu être lus."
        details "Erreur" "$LOG_DIR/dependencies.md"
        return
    fi
    if [[ ! -s "$LOG_DIR/dependencies.md" ]]; then
        echo "➖ Aucune."
        return
    fi
    echo "⚠️ À justifier dans leur commit (maintenue, licence, sans équivalent, nom sûr) :"
    cat "$LOG_DIR/dependencies.md"
}

{
    echo "## Rapport de la CI"
    echo
    rules_section
    echo
    tests_section
    echo
    routes_section
    echo
    migrations_section
    echo
    dependencies_section
} >"$REPORT"
