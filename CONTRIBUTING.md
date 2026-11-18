# Contribuer à Learnagement

Learnagement est à la fois un outil en production, utilisé par les enseignants, les étudiants et
les administratifs, et un projet où l'on apprend. Ce guide dit comment contribuer aujourd'hui ;
[l'architecture cible](docs/architecture.md) dit où va le repo, avec un `lab/` pour apprendre
dans le langage de son choix (T-50).

## Démarrer

1. Installer Docker, Python 3.12 ou plus et [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Lancer l'application : `python3 bootstrap.py` (le [README](README.md) détaille les modes).
3. Installer une fois les vérifications de commit : `uvx pre-commit install`.
4. Se connecter avec un utilisateur de test du jeu de données libres « small » (liste dans le
   README) : jamais avec des données réelles.

## Choisir quoi faire

- Le [backlog](docs/backlog/backlog.md) est la seule liste du travail à faire. Un ticket dont
  l'`Owner` est `—` est libre : y écrire son login GitHub pour le prendre.
- Avant de nommer quoi que ce soit, lire le [glossaire](docs/glossary.md) : le code parle anglais,
  avec les mots du métier, et les textes de l'interface restent en français.
- La carte du repo est dans le [CLAUDE.md](CLAUDE.md) : elle dit où se trouve chaque chose.

## Branches et commits

- Une branche par sujet, partie de `dev`, nommée selon [docs/git.md](docs/git.md) ; jamais de
  commit direct sur `main`, `prerelease` ou `dev`.
- Des commits petits et atomiques : 10 fichiers au plus, un titre de 50 caractères au plus,
  préfixé par son type (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`…), en français.
- Une migration de base ne se mélange jamais à du code métier dans un même commit.

## Les règles

Les règles de code sont dans la [charte](.claude/rules/ion-repo/charter.md) et les fichiers voisins
(Python, FastAPI, Next, sécurité, production). Une partie est vérifiée à chaque commit et en CI :

| Partie | Vérifié aujourd'hui |
|---|---|
| `backend/` | ruff, couches (import-linter), `openapi.json` réécrit d'après le code, charte |
| `launcher/`, `scraping/`, `dashboards/` | ruff (lint et mise en forme), charte |
| `frontend/` | ESLint, charte |
| `web/` (PHP) | PHP-CS-Fixer, PHPStan, couches (deptrac), pas de SQL dans une page, charte |
| `web/` (JavaScript) | ESLint, Prettier, charte |
| tout le repo | gros fichiers, conflits, clés privées, secrets |

Chaque outil part du niveau qui passe aujourd'hui ; la dette restante est écrite dans sa
configuration (`web/.php-cs-fixer.dist.php`, `web/phpstan-baseline.neon`, `web/.prettierignore`,
`backend/pyproject.toml`) et ne fait que baisser. Le PHP se vérifie sans PHP installé :
`web/tools/run.sh` passe alors par podman (`web/tools/run.sh vendor/bin/phpstan analyse`). Le
JavaScript de `web/` a ses tests, lancés par Node sans navigateur ni serveur, l'API simulée :
`pnpm --dir web test` (`web/tests/`), pas encore en CI.

En CI s'ajoutent les tests et le typage du backend, le contrat de l'API (`openapi.json` et les
routes cassées par rapport à `main`), le lint, le typage et la compilation du front, et l'audit
des dépendances.

## Ouvrir une pull request

- Remplir le modèle de PR : quoi, pourquoi, comment tester.
- La CI commente la PR : règles, tests, routes cassées, migrations et nouvelles dépendances ; le
  commentaire se met à jour à chaque poussée.
- Une PR courte, sur un seul sujet ; un bug corrigé arrive avec le test qui l'aurait détecté.
- Aucun secret ni donnée personnelle réelle dans le diff, les logs ou les captures.
- Une route de l'API, une variable d'environnement ou une commande du lanceur ne change pas sans
  une ligne dans la section « Changements d'interface » du README : d'autres étudiants s'en
  servent.
- Flavien Vernier relit et merge seul : plus la PR est courte et vérifiée, plus elle passe vite.
