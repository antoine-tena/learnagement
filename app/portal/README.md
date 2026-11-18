# La porte d'entrée

La seule entrée de l'application, à construire avec learnagement#T-41 : un seul domaine, des
chemins au lieu de ports (`/` pour le web, `/api/`, `/dashboards/`, `/assistant/`), la connexion
CAS ouverte une fois par l'API, et un proxy (Caddy) qui vérifie la session avant de servir une
page. Le détail : [architecture](../../docs/architecture.md), « La porte d'entrée ».

Aujourd'hui, chaque application a son port et le web redirige vers les autres
(`app/web/views/dashboard/python.php`).
