#!/usr/bin/env bash
# La sauvegarde quotidienne de la base, dans le conteneur data_mysql_backup.
#
#   backup.sh          tourne sans fin : une sauvegarde par jour à BACKUP_AT
#   backup.sh once     une sauvegarde tout de suite, puis s'arrête
#   backup.sh health   la sonde de santé : échoue si la dernière sauvegarde a raté
#                      ou date de plus de BACKUP_MAX_AGE_HOURS
#
# Chaque sauvegarde est un seul fichier, cohérent (--single-transaction) et compressé :
# /backup/learnagement_<AAAAMMJJ-HHMMSS>.sql.gz, écrit sous un nom temporaire puis renommé.
# L'état est dans /state : last_success (epoch de la dernière réussite), last_error.
set -euo pipefail
umask 077 # les sauvegardes contiennent des données personnelles

BACKUP_DIRECTORY=/backup
STATE_DIRECTORY=/state
BACKUP_PREFIX=learnagement_
DEFAULT_RETENTION_DAYS=30
DEFAULT_MAX_AGE_HOURS=26
SECONDS_PER_HOUR=3600

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') [backup] $*"; }

is_enabled() {
    case "${BACKUP:-false}" in
        1 | true | yes | y | on | oui) return 0 ;;
        *) return 1 ;;
    esac
}

dump_database() {
    local target="$1"
    MYSQL_PWD="$MYSQL_USER_PASSWORD" mysqldump \
        -h "$MYSQL_SERVER" -u "$MYSQL_USER_LOGIN" \
        --single-transaction --triggers --no-tablespaces --skip-comments \
        "$MYSQL_DB" | gzip -9 >"$target"
}

purge_old_backups() {
    local days="${BACKUP_RETENTION_DAYS:-$DEFAULT_RETENTION_DAYS}"
    find "$BACKUP_DIRECTORY" -maxdepth 1 -name "${BACKUP_PREFIX}*.sql.gz" \
        -mtime "+$days" -print -delete | sed 's/^/[backup] supprimée : /'
}

alert() {
    local message="$1"
    echo "$(date +%s) $message" >"$STATE_DIRECTORY/last_error"
    log "ÉCHEC : $message"
    if [[ -n "${BACKUP_ALERT_URL:-}" ]]; then
        curl -fsS -m 30 --data-urlencode "message=Learnagement : $message" \
            "$BACKUP_ALERT_URL" >/dev/null || log "alerte non envoyée à BACKUP_ALERT_URL"
    fi
}

backup_once() {
    local stamp target part
    stamp="$(date '+%Y%m%d-%H%M%S')"
    target="$BACKUP_DIRECTORY/${BACKUP_PREFIX}${stamp}.sql.gz"
    part="$target.part"
    if ! dump_database "$part" || ! gzip -t "$part"; then
        rm -f "$part"
        alert "sauvegarde du $stamp ratée"
        return 1
    fi
    mv "$part" "$target"
    date +%s >"$STATE_DIRECTORY/last_success"
    rm -f "$STATE_DIRECTORY/last_error"
    log "sauvegarde écrite : $(basename "$target") ($(du -h "$target" | cut -f1))"
    purge_old_backups
}

seconds_until_next_run() {
    local at="${BACKUP_AT:-00:00}" now next
    now="$(date +%s)"
    next="$(date -d "today $at" +%s)"
    if ((next <= now)); then
        next="$(date -d "tomorrow $at" +%s)"
    fi
    echo $((next - now))
}

health() {
    is_enabled || return 0
    [[ ! -f "$STATE_DIRECTORY/last_error" ]] || return 1
    local last max_age
    last="$(cat "$STATE_DIRECTORY/last_success" 2>/dev/null || echo 0)"
    max_age=$((${BACKUP_MAX_AGE_HOURS:-$DEFAULT_MAX_AGE_HOURS} * SECONDS_PER_HOUR))
    (($(date +%s) - last < max_age))
}

run_forever() {
    if ! is_enabled; then
        log "désactivée (BACKUP n'est pas à true)"
        exec sleep infinity
    fi
    date -d "today ${BACKUP_AT:-00:00}" >/dev/null || {
        log "BACKUP_AT invalide : '${BACKUP_AT:-}' (attendu HH:MM)"
        exit 1
    }
    [[ -f "$STATE_DIRECTORY/last_success" ]] || backup_once || true
    while true; do
        local delay
        delay="$(seconds_until_next_run)"
        log "prochaine sauvegarde dans $((delay / 60)) min (à ${BACKUP_AT:-00:00})"
        sleep "$delay"
        backup_once || true
    done
}

mkdir -p "$STATE_DIRECTORY"
case "${1:-}" in
    once) backup_once ;;
    health) health ;;
    "") run_forever ;;
    *)
        echo "usage : backup.sh [once|health]" >&2
        exit 2
        ;;
esac
