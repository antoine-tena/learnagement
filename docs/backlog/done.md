# Done

The closed tickets of Learnagement, most recent first, one line each:
`- **YYYY-MM-DD** · T-NN · Title — what was done (branch) · opened YYYY-MM-DD`.

- **2026-10-30** · T-30 · `scraping/` en vrai paquet testé — paquet et commande uniques, requêtes paramétrées, 28 tests sur pages fictives ; `recup_agenda.py` et `filling_etudiant_db.py`, inachevés, retirés ; stages exportés sans écriture en base ; jamais lancé sur les vrais sites (refactor/scraping-package) · opened 2026-10-30
- **2026-10-30** · T-10 · La doc rangée dans `docs/`, les `.env` d'exemple nommés clairement — `Doc/`, `GIT.md`, `PERMISSIONS.md` dans `docs/`, `ToDo/` versé dans le backlog, modèles dans `config/` ; README : seuls ses liens changent, uv et podman restent à T-05 et T-06 (chore/tidy-tree) · opened 2026-10-30
- **2026-10-30** · T-14 · Next.js à jour : la faille du middleware corrigée — contournement reproduit sur 15.1.2 (200) puis bloqué (307) ; Next 16.4.3, ESLint, `proxy.ts`, pnpm seul, Node 24 dans le conteneur, build de production qui passe (fix/next-16-pnpm) · opened 2026-10-30
- **2026-10-30** · T-17 · L'API passe ruff : format, imports, annotations — ruff check et format propres sur backend/, routes et JSON inchangés (style/backend-ruff) · opened 2026-10-30
- **2026-10-30** · T-02 · Le front PHP passe par l'API, plus par la base — déjà fait par Flavien (tous les accès SQL du front sont commentés) ; connectDB.php, qui ne faisait plus que recharger le .env, archivé ; connexion par le front PHP vérifiée (fix/sql-parameters) · opened 2026-10-30
- **2026-10-30** · T-01 · Requêtes SQL de l'API construites avec des paramètres — faux positif : les requêtes signalées étaient du code commenté, et les requêtes actives passent toutes par des paramètres liés ; vérifié à la main (fix/sql-parameters) · opened 2026-10-30
- **2026-10-30** · T-04 · L'arborescence suit kiln : `backend/`, `frontend/` — `backend/` (FastAPI), `frontend/` (Next), `web/`, `dashboards/`, `scraping/`, `launcher/` ; `kiln set backend=fastapi frontend=next`, lockfiles (refactor/layout) · opened 2026-10-30
- **2026-10-30** · T-03 · Le code mort rangé dans `archive/` — `phpbackend/` et deux scripts jamais appelés déplacés, `archive/` exclu de la charte (chore/archive) · opened 2026-10-30
