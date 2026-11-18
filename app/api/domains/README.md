# domains

Les routes et requêtes métier de l'API, un domaine par module ou par paquet. Chaque domaine expose
un `router` FastAPI que `app.py` monte ; les routes générées et la documentation sont sur
`/api/docs` une fois l'instance lancée, et dans `app/api/openapi.json`.

## Les domaines

| Domaine | Ce qu'il sert |
| --- | --- |
| `lnm_university/` | La mobilité côté étudiant et gestionnaire : universités partenaires, campagne, vœux, affectations, exports. |
| `lnm_mobility_assignment/` | L'affectation automatique des places de mobilité (`algorithm.py`) et les quotas. |
| `maquette_module/` | Les modules de la maquette : vue d'ensemble, intervenants, enchaînement et dépendances (Gantt), modifications. |
| `maquette_module_creation.py` | La création d'un module (`POST /modules`). |
| `lnm_etudiant/` | Les étudiants : liste, parcours, stages. |
| `lnm_enseignant.py` | Les enseignants : service, modules, charge. |
| `lnm_evaluation/` | Les évaluations et les compétences évaluées. |
| `lnm_rendu_module.py` | Les rendus de module vus par un enseignant. |
| `lnm_calendar.py` | Le calendrier des séances. |
| `lnm_filiere.py` | Les filières et statuts, en routes générées. |
| `apc_competence.py`, `apc_data.py`, `apc_kpi_competence.py` | L'approche par compétences : référentiel, données et indicateurs pour les tableaux de bord. |
| `account_activation/` | L'activation des comptes internes par un lien à usage unique. |

Le sens de chaque mot (étudiant, maquette, rendu…) : le [glossaire](../../../docs/glossary.md).

## La forme d'un domaine en paquet

- `__init__.py` : rassemble les routeurs des modules en un seul `router`.
- `*_routes.py` ou un module par sujet : les routes, minces.
- `queries.py` ou `_db.py` : le SQL et l'accès à la base.
- `schemas.py` : les modèles pydantic des entrées et des sorties.
- `service.py` quand la logique dépasse une requête.

Un domaine qui grossit au-delà de 300 lignes devient un paquet de cette forme.

## Ajouter un domaine

1. Créer `domains/<nom_du_glossaire>/` (snake_case ; les tables SQL gardent leur casse).
2. Protéger chaque route : utilisateur courant par dépendance (`api/dependencies/`), règle
   d'accès évaluée par `access_control/`.
3. Monter le `router` dans `app.py`.
4. Écrire ses tests dans `app/api/tests/`, puis régénérer le schéma :
   `uv run python -m tools.export_openapi --output openapi.json` depuis `app/api/`.

Une route publiée est une interface : la changer se signale dans le [README](../../../README.md).
Les couches permises entre dossiers sont vérifiées par import-linter (`pyproject.toml`).
