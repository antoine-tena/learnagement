# Learnagement

Outil d'intégration des données de l'enseignement de l'USMB : le pont entre étudiants,
enseignants et administratifs (planning prévisionnel, cohérence MCCC, absences, stages, mobilité).
Développé surtout par des étudiants (IDU de Polytech Annecy, Licence SCEM), sous la
responsabilité de Flavien Vernier.

<!-- This file belongs to the project: kiln wrote it once and never changes it. kiln's rules live
in .claude/rules/kiln/ and are kept current by `kiln update`. Write here what Claude cannot
guess about this project, and keep it under 200 lines: every session reads it. -->

## Carte du repo

À lire avant d'ouvrir des fichiers ; à mettre à jour dans le commit qui ajoute, déplace ou
supprime un dossier, un domaine ou un point d'entrée.

- `Learnagement.py` : le lanceur (click) : `start`, `stop`, `generate-env`, `backupdb`,
  `exportinstance`… ; il s'appuie sur `env.py` (génération et propagation des `.env`),
  `config.py` (conteneurs, environnements), `tools.py`, `bootstrap.py`, `docker-compose.py` et
  `Learnagement_Security.py` (certificats).
- `docker/` : un dossier par conteneur (Dockerfile, entrypoint) et
  `docker-compose.yml.skeleton`, d'où le lanceur produit `docker/docker-compose.yml` (ignoré).
- `backend_python/` : l'API FastAPI (`app.py`) ; `api/` (routes, `dependencies.py`), `auth/`
  (LNM et CAS), `access_control/` (règles, prédicats, responsabilités), `user/` (requêtes
  métier par domaine : `LNM_university.py`, `MAQUETTE_module.py`…), `models/`, `db/`
  (connexion SQLAlchemy), `tests/` (pytest).
- `front_PHP/` : le front principal (Apache) ; `index.php` + `utils/router.php`, `views/`
  (pages), `components/`, `utils/apiProxy.php` (appels à l'API Python), `theme/`, `assets/`.
- `front_DashPlotly/` : les tableaux de bord Dash (`main.py`, une app `appNN_*` par vue et son
  `_tools.py`), `apc_dash/` (approche par compétences).
- `front_NextJS/` : le front Next.js en cours de refonte (`app/`, proxy vers l'API Python).
- `archive/` : le code mort gardé pour mémoire (ancien backend PHP…), hors des règles ; son
  `README.md` dit ce que chaque chose était.
- `db/` : `sql/` (schéma, migrations versionnées `VX.Y.Z__*.sql`), `freeData/` (jeux de données
  libres), `tools/`, `update/` ; `db/data/` et `db/backup/` sont privés et ignorés.
- `scrapping/` : scripts d'import (notes, agenda, stages, étudiants…).
- `Doc/`, `ToDo/` : documentation et listes de tâches historiques.
- `docs/backlog/` : le travail à faire ; `charter.toml` : les règles vérifiées ;
  `.claude/rules/kiln/` : les règles de kiln pour Claude.

## Notes

- Les branches de Flavien : `main` (production), `prerelease`, `dev` (intégration), puis
  `feature/`, `bugfix/`, `refactor/`… (`GIT.md`). Le fork `antoine-tena/learnagement` intègre
  sur `antoine-tena`, puis propose ses changements à `dev` en pull request.
- Les `.env` sont générés par le lanceur à partir de `__env_skeleton.env` et
  `__env_default_<env>.env`, puis recopiés dans chaque conteneur : on ne les édite jamais à la
  main dans les sous-dossiers.
- Des étudiants travaillent sur le repo par promotion : on ne casse pas une interface (route de
  l'API, variable d'environnement, commande du lanceur) sans le signaler dans le README.
