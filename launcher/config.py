# Couleurs pour les messages (non directement nécessaires dans Python mais émulation via ANSI codes)
# Blue='\033[0;34m'
# Purple='\033[0;35m'
# Cyan='\033[0;36m'
# White='\033[0;37m'
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
NC = "\033[0m"  # No color

# Les conteneurs de chaque environnement, un fragment compose chacun (COMPOSE_FRAGMENTS).
# Dans aucune liste pour l'instant : `etl` (Mage AI), premier essai.
CONTAINERS = {
    "dev": ["data_mysql", "phpmyadmin", "backend", "web", "dashboards", "frontend"],
    "prod": ["data_mysql", "data_mysql_backup", "backend", "web", "dashboards"],
}
# Le dossier où chaque conteneur lit son .env (None : il n'en lit pas)
CONTAINER_APP_DIRS: dict[str, str | None] = {
    "data_mysql": "database",
    "data_mysql_backup": None,
    "etl": None,
    "phpmyadmin": None,
    "backend": "app/api",
    "web": "app/web",
    "dashboards": "app/dashboards",
    "frontend": "frontend",
}
# Le fragment compose de chaque conteneur : le `compose.yaml` d'une application, dans son
# dossier, ou celui d'un service de la base et de l'exploitation, dans `docker/compose/`
COMPOSE_FRAGMENTS = {
    "data_mysql": "docker/compose/data_mysql.yml",
    "data_mysql_backup": "docker/compose/data_mysql_backup.yml",
    "etl": "docker/compose/etl.yml",
    "phpmyadmin": "docker/compose/phpmyadmin.yml",
    "backend": "docker/compose/backend.yml",
    "web": "docker/compose/web.yml",
    "dashboards": "docker/compose/dashboards.yml",
    "frontend": "docker/compose/frontend.yml",
}
# compose lit aussi son .env, pour les variables qu'il interpole
COMPOSE_DIR = "docker"
envs = {"dev", "prod"}
