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

- `Learnagement.py` : point d'entrée du lanceur (`python Learnagement.py start`, `stop`,
  `generate-env`, `backupdb`…), dont le code est dans `launcher/` : `cli.py` (les commandes
  click), `env.py` (génération et propagation des `.env`), `config.py` (conteneurs,
  environnements), `security.py` (certificats : `python -m launcher.security`), `tools.py`.
  `bootstrap.py` crée le venv et lance `Learnagement.py`.
- `docker/` : un dossier par conteneur (`backend/`, `web/`, `frontend/`, `dashboards/`,
  `phpmyadmin/` : Dockerfile, entrypoint) et `docker-compose.yml.skeleton`, d'où le lanceur
  produit `docker/docker-compose.yml` (ignoré).
- `backend/` : l'API FastAPI (`app.py`) ; `api/` (routes, `dependencies.py`), `auth/` (LNM et
  CAS), `access_control/` (règles, prédicats, responsabilités), `domains/` (requêtes métier par
  domaine : `lnm_university.py`, `maquette_module.py`…, en snake_case ; les tables SQL gardent leur casse), `models/`, `db/` (connexion
  SQLAlchemy), `tests/` (pytest).
- `web/` : le front principal, en PHP (Apache) ; `index.php` + `utils/router.php`, `views/`
  (pages), `components/`, `utils/apiProxy.php` (appels à l'API), `theme/`, `assets/`.
- `dashboards/` : les tableaux de bord Dash (`main.py`, une app `appNN_*` par vue et son
  `_tools.py`), `apc_dash/` (approche par compétences).
- `frontend/` : le front Next.js en cours de refonte (`app/`, proxy vers l'API).
- `scraping/` : scripts d'import (notes, agenda, stages, étudiants…).
- `db/` : `sql/` (schéma, migrations versionnées `VX.Y.Z__*.sql`), `freeData/` (jeux de données
  libres), `tools/` ; `db/data/` et `db/backup/` sont privés et ignorés.
- `archive/` : le code mort gardé pour mémoire (ancien backend PHP…), hors des règles ; son
  `README.md` dit ce que chaque chose était.
- `docs/` : la documentation (`README.md` en est l'index), `docs/mobility/` pour le module de
  mobilité.
- `docs/backlog/` : le travail à faire ; `charter.toml` : les règles vérifiées ;
  `.claude/rules/kiln/` : les règles de kiln pour Claude.

## Notes

- Les branches de Flavien : `main` (production), `prerelease`, `dev` (intégration), puis
  `feature/`, `bugfix/`, `refactor/`… (`docs/git.md`). Le fork `antoine-tena/learnagement` intègre
  sur `antoine-tena`, puis propose ses changements à `dev` en pull request.
- Les `.env` sont générés par le lanceur à partir de `config/env.skeleton` et
  `config/env.<env>`, puis recopiés dans chaque conteneur : on ne les édite jamais à la
  main dans les sous-dossiers.
- Des étudiants travaillent sur le repo par promotion : on ne casse pas une interface (route de
  l'API, variable d'environnement, commande du lanceur) sans le signaler dans le README.
