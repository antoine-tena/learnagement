# Les tableaux de bord

Les tableaux de bord Dash, ouverts depuis le web avec le jeton LNM de l'utilisateur. Ils ne lisent
jamais la base : ils appellent l'API.

- `main.py` : l'application ; `main_app/` : sa mécanique (pages, connexion, serveur).
- `pages/` : une page par vue, avec son `_tools.py` ; les paquets pour les pages découpées.
- `apc_dash/` : l'approche par compétences, dont l'assistant qui lit les PDF (`polytech_rag/`).
- `clock.py` : la date du jour, à Paris.
- `Containerfile`, `container/`, `compose.yaml` : son conteneur, lancé par le lanceur.

```bash
cd app/dashboards
uv run ruff check . && uv run mypy . && uv run pytest
```
