# Learnagement

Outil d'intégration des données de l'enseignement de l'USMB : le pont entre étudiants,
enseignants et administratifs (planning prévisionnel, cohérence MCCC, absences, stages, mobilité).
Développé surtout par des étudiants (IDU de Polytech Annecy, Licence SCEM), sous la
responsabilité de Flavien Vernier.

<!-- This file belongs to the project: ion-repo wrote it once and never changes it. ion-repo's rules live
in .claude/rules/ion-repo/ and are kept current by `ion repo update`. Write here what Claude cannot
guess about this project, and keep it under 200 lines: every session reads it. -->

## Carte du repo

À lire avant d'ouvrir des fichiers ; à mettre à jour dans le commit qui ajoute, déplace ou
supprime un dossier, un domaine ou un point d'entrée.

- `Learnagement.py` : point d'entrée du lanceur (`python Learnagement.py start`, `stop`,
  `generate-env`, `backupdb`…), dont le code est dans `launcher/` : `cli.py` (les commandes
  click), `instance.py` (changer d'environnement, remise à zéro, export, import), `docker.py` et
  `compose.py` (commandes compose, `compose.yaml` assemblé, attente des sondes), `db.py`
  (initialisation, administrateur, sauvegardes), `fake_data/` (le générateur de données fictives,
  commande `fake-data`, proposé au premier lancement hors production), `backups/` (ancienne sauvegarde planifiée en Python,
  pas branchée), `env.py` (génération et propagation des `.env`), `git.py` (commit dans `.env.git`),
  `config.py` (conteneurs par environnement), `dev_hooks.py` (hooks de pré-commit, posés par
  `bootstrap.py`), `security.py` (certificats :
  `python -m launcher.security`), `tools.py`, `tests/`.
  `bootstrap.py` lance `Learnagement.py` avec `uv run`. Chaque composant Python (la racine pour
  le lanceur, `backend/`, `dashboards/`, `scraping/`, `assistant/`) a son `pyproject.toml` et son `uv.lock`.
- `docker/` : un dossier par conteneur (`backend/`, `web/`, `frontend/`, `dashboards/`,
  `phpmyadmin/` : Containerfile, entrypoint), `backup/` (`backup.sh`, la sauvegarde quotidienne
  de la prod) et `compose/` (un fragment par conteneur), d'où le
  lanceur produit `docker/compose.yaml` (ignoré).
- `backend/` : l'API FastAPI (`app.py`) ; `api/` (routes, `dependencies/`), `auth/` (LNM et
  `authenticate_cas/`), `access_control/` (règles, prédicats, responsabilités), `domains/` (requêtes métier par
  domaine : `lnm_university/`, `maquette_module/`, `lnm_etudiant/`, `lnm_evaluation/`, `lnm_mobility_assignment/`…, en snake_case ; les tables SQL gardent leur casse), `models/`, `db/` (connexion
  SQLAlchemy), `tools/` (`export_openapi.py` : le schéma `openapi.json` de la racine), `tests/`
  (pytest) ; les couches import-linter sont dans `pyproject.toml`.
- `web/` : le front principal, en PHP (Apache) ; `index.php` + `utils/router.php`, `views/`
  (pages, dont `views/dashboard/mobility-admin/`, `views/dashboard/stage/`), `components/`, `scripts/` (`dependance_module/`, `mobility-admin/`, `mobility-map/` : les deux cartes de mobilité), `utils/apiProxy.php` (appels à l'API), `theme/` (dont `theme/theme/`, `theme/mobility-map-streetview/`), `assets/` ; `tests/` (tests Node du JavaScript,
  `pnpm --dir web test`) ; `tools/run.sh` (PHP, ou podman sans PHP) et la
  configuration de PHP-CS-Fixer, PHPStan, deptrac, ESLint, Prettier (`package.json`).
- `dashboards/` : les tableaux de bord Dash (`main.py`, `clock.py` (date du jour à Paris), `main_app/`, `pages/` : une page par vue (dont les paquets
  `modules_enseignant_edit/`, `stages_administratif/`, `checks_administratif/`) et son `_tools.py`), `apc_dash/` (approche par compétences, dont
  `apc20_chatbot_tools/`, `apc20_competence_ac/`, `apc20_heatmap_apc/`, `apc20_ens_contribution/`, `apc20_ens_fiche_module/`, `apc20_ens_reseau_gaps/`, `apc20_metier_orientation/`, `app_reseaupolytech_etudiant/`, `polytech_rag/` : l'assistant qui lit les PDF, sans index).
- `assistant/` : le paquet `learnagement_assistant`, la recherche vectorielle de l'assistant APC
  (RAG : PDF → morceaux → vecteurs → index FAISS ; commandes `learnagement-assistant-chunks` et
  `-index`), hors de l'image Dash ; pas encore en production.
- `frontend/` : le front Next.js en cours de refonte (`app/`, proxy vers l'API).
- `scraping/` : le paquet `learnagement_scraping` (commande `learnagement-scraping`) : `parsers.py`
  (HTML vers données), `browser.py` (Selenium), `db.py` (écritures), `cli.py` ; `out/` est ignoré.
  `scraping/scripts/` : les scripts autonomes de l'équipe (`ical2json.py` + `ical2json_lib/`
  emplois du temps ADE, `scrape_maquette.py` + `scrape_maquette_lib/` catalogue des formations, `matching_26_27/`).
- `db/` : `sql/` (schéma, migrations versionnées `VX.Y.Z__*.sql`), `freeData/` (jeux de données
  libres), `tools/` ; `db/data/` et `db/backup/` sont privés et ignorés.
- `docs/` : la documentation (`README.md` en est l'index) ; `architecture.md` (la cible : `app/`
  pour la production, `lab/` pour apprendre, et ses étapes), `glossary.md` (le nom de chaque mot
  du métier dans le code), `docs/mobility/` pour le module de mobilité. `CONTRIBUTING.md`, à la
  racine : comment contribuer aujourd'hui.
- `docs/backlog/` : le travail à faire ; `charter.toml` : les règles vérifiées ;
  `.claude/rules/ion-repo/` : les règles d'ion-repo pour Claude.
- `.github/` : `workflows/ci.yml` (la CI d'une release), `pr-report.yml` et `pr-comment.yml` (le
  rapport commenté sur chaque PR), `scripts/` (le calcul de ce rapport).

## Notes

- Les branches de Flavien : `main` (production), `prerelease`, `dev` (intégration), puis
  `feature/`, `bugfix/`, `refactor/`… (`docs/git.md`). Le fork `antoine-tena/learnagement` intègre
  sur `antoine-tena`, puis propose ses changements à `dev` en pull request.
- Les `.env` sont générés par le lanceur à partir de `config/env.skeleton` et
  `config/env.<env>`, puis recopiés dans chaque conteneur : on ne les édite jamais à la
  main dans les sous-dossiers.
- Des étudiants travaillent sur le repo par promotion : on ne casse pas une interface (route de
  l'API, variable d'environnement, commande du lanceur) sans le signaler dans le README.
- Un nom dans le code (variable, fonction, fichier, dossier) prend le mot de `docs/glossary.md` ;
  un mot qui manque y est ajouté dans le même commit.
