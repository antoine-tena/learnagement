

# Couleurs pour les messages (non directement nécessaires dans Python mais émulation via ANSI codes)
# Blue='\033[0;34m'
# Purple='\033[0;35m'
# Cyan='\033[0;36m'
# White='\033[0;37m'
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW='\033[0;33m'
NC = "\033[0m"  # No color
containers_system = ["docker", "backend", ] # system docker
containers_prod = ["web", "dashboards", ] # available in prod and dev
containers_dev = ["frontend", ] # available only in dev
envs = {"dev", "prod"}
