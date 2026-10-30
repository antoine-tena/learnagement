# Backlog

Tout ce qui reste à faire sur Learnagement, en une seule liste ordonnée par priorité. Commencé
le **2026-10-30**. Comment écrire un ticket : [README.md](README.md) ; les tickets fermés sont
dans [done.md](done.md), ce qui a été écarté dans [rejected.md](rejected.md). **Rien d'autre
n'est ouvert.**

North star: **Learnagement in service**.

**Next free: T-13.**

---

## 🔴 Critical

### T-01 · Requêtes SQL de l'API construites avec des paramètres
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: `kiln score`, règle SQL-PARAMETERS

`backend_python/api/dependencies.py` (l. 40 à 110) insère des valeurs dans le texte SQL :
injection possible. Passer par les paramètres liés de SQLAlchemy (`text(...)` + `:nom`), un
test par requête.

### T-02 · Le front PHP passe par l'API, plus par la base
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: lecture du code

`front_PHP/utils/connectDB.php`, `views/base/@post/inscription.php`,
`views/dashboard/@post/dependance_module.php`, `views/dashboard/create_stage.php` parlent à
MySQL en direct : deux chemins vers les données, deux contrôles d'accès. Les faire passer par
`utils/apiProxy.php` et une route de l'API.

## 🟠 Important

### T-03 · Le code mort rangé dans `archive/`
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: lecture du code

`phpbackend/` (plus lancé depuis février 2026, remplacé par `backend_python/`), les exemples et
doublons (`front_DashPlotly/multi_page_integration_example.py`, `scrapping/testIcal.py`…) vont
dans `archive/`, hors des règles de kiln, sans être supprimés.

### T-04 · L'arborescence suit kiln : `backend/`, `frontend/`
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: `kiln adopt` (« no stack of kiln found »)

kiln reconnaît une pile dans `backend/` et `frontend/` : `backend_python/` → `backend/`
(FastAPI), `front_NextJS/` → `frontend/` (Next), puis `kiln set backend=fastapi
frontend=next`. Les autres composants prennent des noms simples : `front_PHP/` → `web/`,
`front_DashPlotly/` → `dashboards/`, `scrapping/` → `scraping/`, le lanceur dans `launcher/`.
Chemins mis à jour dans le lanceur, `docker/`, le README.

### T-05 · uv partout : `pyproject.toml` et `uv.lock`
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: charte UV-PODMAN, `kiln score` LOCKED-DEPENDENCIES et NO-OBSOLETE-BACKPORTS

Les `requirements*.txt` deviennent un `pyproject.toml` par composant Python avec son `uv.lock`;
`typing`, `pip`, `setuptools` sortent des dépendances ; `requirements-click-gui.txt` demande
`click-gui-runner`, absent de PyPI. Les conteneurs installent avec `uv sync --frozen`.

### T-06 · Conteneurs : podman, utilisateur non root, images épinglées, sondes
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: charte UV-PODMAN, `kiln score` IMAGES-BY-DIGEST, NON-ROOT-CONTAINERS, HEALTH-PROBES,
  SUPPORTED-RUNTIMES

`Containerfile` et `compose.yaml` (lus par podman comme par docker), lanceur par défaut sur
`podman compose`, `USER` non root, images de base par digest, `HEALTHCHECK` par service,
Node 18 (fin de vie) → Node LTS.

## 🟡 Normal

### T-07 · Le lanceur fonctionne et se lit
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: lancement de référence du 2026-10-30

`start --docker_option=-d` plante (`TypeError: can only concatenate list (not "str") to
list`). `Learnagement.py` (715 lignes) se découpe par commande ; les mots de passe ne passent
plus en argument de `mysqldump`.

### T-08 · Python : plus d'`except:` nu ni de date sans fuseau
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: `kiln score`, règles BARE-EXCEPT et NAIVE-DATETIMES

9 `except:` et 11 `datetime.now()` sans fuseau (dashboards, scraping, API, lanceur).

### T-09 · Front Next : ESLint et plus d'`any`
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: `kiln score`, règles JS-LINTER et NO-ANY

### T-10 · La doc rangée dans `docs/`, les `.env` d'exemple nommés clairement
- **Type**: task
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: lecture du repo

`Doc/` → `docs/`, les six `ToDo.md` versés en tickets ici, `GIT.md`, `PERMISSIONS.md` dans
`docs/`. README à jour (uv, podman, nouvelle arborescence).

### T-11 · Les fichiers géants découpés
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: charte FILE-SIZE

`LNM_university.py` (1 868 lignes), `MAQUETTE_module.py` (1 067), `mobility-admin.php`
(2 953), les deux cartes de mobilité presque identiques (`mobility-map.php`,
`mobility-map_open.php`). Un module par domaine, tests d'abord (`/kiln:modernize`).

## ⚪ Background — long-running work, debt and ideas

### T-12 · Un seul front à terme
- **Type**: idea
- **Status**: blocked — waiting for Flavien
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: lecture du repo

Trois fronts (PHP, Dash, Next) pour une seule application. Flavien a une branche
`refactor/nextJS_front` : décider avec lui la cible et le calendrier.
