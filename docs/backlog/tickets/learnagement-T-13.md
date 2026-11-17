# learnagement#T-13 · Logs de l'API en structlog
- **Type**: improvement
- **Priority**: 🟡 normal
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: charte LOGGING (exception temporaire dans `waivers.toml`)

`logging.getLogger` dans 15 modules de `backend/` et `print()` dans `app.py`, `init.py`,
`system/access_auth.py` : un `structlog` configuré dans `core/logging.py`, des événements
`domaine.evenement` avec leurs champs. Retirer l'exception LOGGING à la fin.
