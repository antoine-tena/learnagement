# app

Ce qui tourne en production, chez les enseignants, les étudiants et les administratifs : une
application par dossier. Pour apprendre ou essayer, c'est [`lab/`](../lab/README.md).

| Dossier | Langage | Rôle |
| --- | --- | --- |
| [`api/`](api/README.md) | Python, FastAPI | Le cœur : la seule application qui lit et écrit la base. |
| [`web/`](web/README.md) | PHP, Apache | Les pages principales ; passe par l'API (`utils/apiProxy.php`). |
| [`dashboards/`](dashboards/README.md) | Python, Dash | Les tableaux de bord (charge, absences, notes, stages, APC). |
| [`assistant/`](assistant/README.md) | Python | La recherche vectorielle de l'assistant APC ; pas encore en production. |
| [`importers/`](importers/README.md) | Python | L'import des données externes (ADE, catalogue USMB). |
| [`portal/`](portal/README.md) | à choisir | La porte d'entrée (connexion CAS, routes), à construire (learnagement#T-41). |

## Ce que chaque application porte

- `Containerfile` et `.containerignore` : son image.
- `container/` : l'entrypoint et la configuration copiée dans l'image.
- `compose.yaml` : son fragment, que le lanceur assemble dans `deploy/compose.yaml` (chemins
  relatifs à `deploy/`).
- `pyproject.toml` et `uv.lock` pour les applications Python.

On ne lance pas une application seule : `python Learnagement.py start` démarre l'ensemble.

## Les règles

- La base n'est joignable que par l'API : ni `web/` ni `dashboards/` ne contiennent de SQL.
- Un domaine porte le même nom dans chaque application, d'après le
  [glossaire](../docs/glossary.md).
- Changer une route de l'API, c'est casser le travail d'une autre promo : on le signale dans le
  [README](../README.md).

La cible et ses étapes : [docs/architecture.md](../docs/architecture.md).
