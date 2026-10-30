# Backlog

Tout ce qui reste à faire sur Learnagement, en une seule liste ordonnée par priorité. Commencé
le **2026-10-30**. Comment écrire un ticket : [README.md](README.md) ; les tickets fermés sont
dans [done.md](done.md), ce qui a été écarté dans [rejected.md](rejected.md). **Rien d'autre
n'est ouvert.**

North star: **Learnagement in service**.

**Next free: T-21.**

---

## 🔴 Critical



## 🟠 Important

### T-18 · Plus de données personnelles dans les logs du front
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: T-14, lecture de `route.ts`

`app/api/auth/[...nextauth]/route.ts` écrit l'email, le prénom et le nom de l'utilisateur dans
les logs à chaque connexion ([PERSONAL-DATA]) : ne garder que l'identifiant.

### T-19 · Zod 4 et audit des dépendances du front
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: `pnpm audit` après T-14

`pnpm audit` signale encore zod < 4.6.6 (élevée, dépendance directe en 3.x, version majeure à
passer), postcss-selector-parser par `@tailwindcss/typography` (modérée) et deepmerge par
`@svgr/webpack` (faible, sans correctif).


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

### T-20 · Le front passe ESLint
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: ESLint installé par T-14

Le hook de commit vérifie chaque fichier touché, et `eslint .` trouve encore des erreurs
anciennes dans tout `frontend/` (`any`, `set-state-in-effect`, `prefer-const`) : le premier qui
modifie un de ces fichiers doit les corriger. À solder d'un coup.

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

### T-13 · Logs de l'API en structlog
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: charte LOGGING (exception temporaire dans `kiln-waivers.toml`)

`logging.getLogger` dans 15 modules de `backend/` et `print()` dans `app.py`, `init.py`,
`system/access_auth.py` : un `structlog` configuré dans `core/logging.py`, des événements
`domaine.evenement` avec leurs champs. Retirer l'exception LOGGING à la fin.

### T-15 · Intitulés de modules abîmés dans les jeux de données
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: renommage des dossiers (grep de `front_DashPlotly`)

`db/freeData/small_set/V0.0.5__data_small.sql` (l. 2999-3000) et
`db/freeData/Polytech_Annecy_Chambery/V0.3.8__data_Polytech_Annecy_Chambery.sql` (l. 569-570) :
« Analyse et front_DashPlotly de données », trace d'un rechercher-remplacer ; sans doute
« Analyse et visualisation de données ». Vérifier avec Flavien, corriger par une migration de
données.

### T-16 · Le mot de passe n'est plus haché dans le navigateur
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: lecture de `frontend/app/activateAccount/page.tsx`

La page d'activation hache le mot de passe avec `bcryptjs` côté client puis envoie le hash : le
hash devient le secret, et le serveur ne contrôle ni le coût ni le sel. Envoyer le mot de passe
en HTTPS, hacher dans l'API (`pwdlib`).

## ⚪ Background — long-running work, debt and ideas

### T-12 · Un seul front à terme
- **Type**: idea
- **Status**: blocked — waiting for Flavien
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: lecture du repo

Trois fronts (PHP, Dash, Next) pour une seule application. Flavien a une branche
`refactor/nextJS_front` : décider avec lui la cible et le calendrier.
