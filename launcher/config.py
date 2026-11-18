# Couleurs pour les messages (non directement nécessaires dans Python mais émulation via ANSI codes)
# Blue='\033[0;34m'
# Purple='\033[0;35m'
# Cyan='\033[0;36m'
# White='\033[0;37m'
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
NC = "\033[0m"  # No color

# Les conteneurs de chaque environnement, un fragment `docker/compose/<conteneur>.yml` chacun.
# Dans aucune liste pour l'instant : `etl` (Mage AI), premier essai.
CONTAINERS = {
    "dev": ["data_mysql", "phpmyadmin", "backend", "web", "dashboards", "frontend"],
    "prod": ["data_mysql", "data_mysql_backup", "backend", "web", "dashboards"],
}
# Le dossier où chaque conteneur lit son .env (None : il n'en lit pas)
CONTAINER_APP_DIRS: dict[str, str | None] = {
    "data_mysql": "db",
    "data_mysql_backup": None,
    "etl": None,
    "phpmyadmin": None,
    "backend": "backend",
    "web": "web",
    "dashboards": "dashboards",
    "frontend": "frontend",
}
# docker compose lit aussi son .env, pour les variables qu'il interpole
COMPOSE_DIR = "docker"
envs = {"dev", "prod"}
