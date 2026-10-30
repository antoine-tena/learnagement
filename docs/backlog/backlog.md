# Backlog

Tout ce qui reste à faire sur Learnagement, en une seule liste ordonnée par priorité. Commencé
le **2026-10-30**. Comment écrire un ticket : [README.md](README.md) ; les tickets fermés sont
dans [done.md](done.md), ce qui a été écarté dans [rejected.md](rejected.md). **Rien d'autre
n'est ouvert.**

North star: **Learnagement in service**.

**Next free: T-39.**

---

## 🔴 Critical



## 🟠 Important

### T-33 · Prévenir les contributeurs du refacto du fork
- **Type**: task
- **Status**: blocked — waiting for @antoine-tena : à lancer seulement sur sa demande
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: @antoine-tena · **Due**: —
- **Origin**: demande d'Antoine, pour que les travaux en cours ne divergent pas du fork

À faire avant T-11 et T-29 : au 2026-10-30, le fork a 70 commits d'avance et 532 fichiers
modifiés par rapport à `dev`, et Flavien travaille surtout dans le backend, sous les anciens
chemins (`backend_python/`). Déplacer encore des fichiers rendrait la PR plus difficile à
intégrer. Lui signaler aussi T-34 et décider avec lui de T-12.

- [ ] En parler d'abord à Flavien : c'est son repo, et le fork lui propose ses changements par
  PR vers `dev`. Il est le seul à pouvoir prévenir les étudiants de cette année qui n'ont encore
  rien poussé.
- [ ] Ouvrir la PR en brouillon vers `dev` :
  https://github.com/FlavienVernier/learnagement/compare/dev...antoine-tena:learnagement:antoine-tena?expand=1
- [ ] Revoir les destinataires et les renommages du message, relevés le 2026-10-30.
- [ ] Poster le message, sous le compte d'Antoine et après son accord sur le texte :
  https://github.com/FlavienVernier/learnagement/issues/new

Les mentions notifient par GitHub, sans chercher d'e-mails dans les commits. Le message ne promet
pas que rien n'est supprimé : le diff compte 33 suppressions (dont `ToDo.md`, anciens scripts de
`scrapping/`) à vérifier, et les branches existantes risquent des conflits.

**Titre** : Refacto de structure en cours : où merger votre travail

> Bonjour @FlavienVernier @Houssam365 @maxencels576,
>
> Je fais une grosse réorganisation du repo sur mon fork, branche
> [`antoine-tena`](https://github.com/antoine-tena/learnagement/tree/antoine-tena) : dossiers
> renommés (`backend_python/` → `backend/`, `front_PHP/` → `web/`, `scrapping/` → `scraping/`…),
> tests et documentation. Le but n'est pas de retirer des fonctionnalités : le code est surtout
> déplacé, et le code mort va dans `archive/`.
>
> Pour éviter que nos travaux divergent, si vous avez du travail en cours, pouvez-vous le merger
> dans ma branche, ou ouvrir une PR vers elle ?
>
> ```
> git remote add antoine https://github.com/antoine-tena/learnagement.git
> git fetch antoine
> git merge antoine/antoine-tena
> ```
>
> Si un conflit vous bloque ou s'il vous manque quelque chose, dites-le ici et je m'en occupe.
> @FlavienVernier, je proposerai l'ensemble à `dev` par PR : dis-moi si tu préfères une autre
> organisation.

### T-34 · Plus de JWT dans les URL
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture

`web/views/dashboard/python.php` et `nextjs.php` redirigent vers Dash et Next avec
`?jwt_token=…` ; `dashboards/apc_dash/apc_hub.py` le conserve dans ses liens. Le jeton peut finir
dans les historiques et les logs. `nextjs.php` force en plus `http` quel que soit l'environnement,
donc le jeton peut circuler en clair.

- [ ] Vérifier le comportement sur une instance en HTTPS (code lu, pas encore lancé).
- [ ] Transmettre l'authentification autrement : cookie `HttpOnly` et `Secure` sur un même domaine
  ou code à usage unique échangé côté serveur.
- [ ] Servir Next en HTTPS.

### T-35 · Le PHP ne parle plus à la base
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture

Quatre fichiers de `web/` exécutent du SQL par `mysqli`, hors de l'API : `views/base/@post/inscription.php`,
`views/dashboard/@post/dependance_module.php`, `views/dashboard/create_stage.php`,
`views/dashboard/rendus-enseignant.php`. Créer les routes manquantes dans le backend, avec leurs
tests et leurs droits, puis les appeler par `utils/apiProxy.php`. C'est le premier pas vers un
seul backend, et il ne dépend pas de T-12.

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

### T-36 · Les appels de Next visent des routes qui existent
- **Type**: bug
- **Status**: to verify — `frontend/app/`
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture

7 appels sur 13 passent par `/api/proxy/list/*` et `/api/proxy/select/*`, pour lesquels une
recherche ne trouve aucune route du backend, sur aucune branche : `listApprentissagesCritiques`,
`listModulesOfAllAPC` (deux appels), `selectChargeEnseignant`, `selectSeance`, `selectMaquette`,
`listAPCbyIdModule`. Sont touchés : les charges, la maquette et une partie des modules. Confirmer
en lançant le front, puis brancher ces écrans sur les routes actuelles ou les créer.

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
plus en argument de `mysqldump`. `launcher/cli.py` et `launcher/env.py` ne passent pas ruff
(58 erreurs, dont 37 `LOG015`, et le format) : le lanceur n'est pas encore dans le pre-commit.

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

### T-11 · Les fichiers géants découpés
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: charte FILE-SIZE

`backend/domains/lnm_university.py` (2 155 lignes, à commencer par lui),
`backend/domains/maquette_module.py` (1 312), `mobility-admin.php` (2 953), les deux cartes de
mobilité presque identiques (`mobility-map.php`, `mobility-map_open.php`). Un module par domaine,
tests d'abord (`/kiln:modernize`), sans changer les routes. Le backend attend T-33 ;
`mobility-admin.php` est migré en dernier (T-12).

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

### T-29 · Le backend découpé par domaine
- **Type**: improvement
- **Status**: blocked — waiting for T-33
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'arborescence, revue de l'architecture

Le backend est déjà presque rangé par domaine : `domains/` a un fichier par domaine, avec ses
routes et son SQL ; `repositories/` n'a qu'un fichier et `models/` trois petits. Il reste à faire
de ces fichiers des paquets aux noms de kiln (`backend/app/<domaine>/api.py`, `services.py`,
règles [ROUTERS] et [SERVICES]), avec T-11, sans changer les routes. Pas d'architecture
hexagonale : seule la logique complexe, comme l'affectation des mobilités, est isolée pour être
testée sans base.

### T-31 · Des noms parlants pour les tableaux de bord
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'arborescence

Les préfixes `appNN_` ne disent rien, et `app11_dag_dependance_new.py` côtoie son ancienne
version. À décider après T-12, qui peut faire disparaître ces apps.

### T-32 · Des tests pour le front et les tableaux de bord
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: revue de l'arborescence

Seul `backend/` a une vraie suite de tests : couvrir au moins les parcours critiques du front
retenu par T-12.

### T-21 · Code, commentaires et doc en anglais
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/ToDo.md`

Tout passer en anglais, sauf l'interface. À décider avec Flavien.

### T-22 · Interface multilingue
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/ToDo.md`

Une option de langue pour l'interface.

### T-23 · Commande du lanceur pour extraire la structure de la base
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/db/ToDo.md`

Extraire la structure avec ses commentaires. `backupDB` existe, mais pas cette commande.

### T-24 · Le rôle étudiant dans la base
- **Type**: task
- **Status**: to verify — `db/sql/`
- **Opened**: 2026-10-30
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/db/ToDo.md`

L'ancienne liste demandait d'ajouter `etudiant` aux rôles : vérifier si c'est encore à faire.

### T-25 · Un utilisateur dans une seule table de personnes
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/db/ToDo.md`

Vérifier qu'un utilisateur n'est présent qu'une fois parmi administratif, enseignant et étudiant.

### T-26 · Commande du lanceur pour mettre à jour MySQL
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/docker/mysql/ToDo.md`

- [ ] Verrouiller l'accès à la base
- [ ] Redémarrer Learnagement

### T-27 · Nommage et structure des tableaux de bord
- **Type**: improvement
- **Status**: to verify — `dashboards/`
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/visualisation/ToDo.md`

L'ancienne liste demandait de revoir le nommage : vérifier ce qu'il reste après T-04.

### T-28 · Connexion des tableaux de bord au standard LNM
- **Type**: improvement
- **Status**: to verify — `dashboards/`
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/visualisation/visus/ToDo.md`

Vérifier que la connexion à la base des tableaux de bord suit le standard LNM.

### T-12 · Une seule API, une seule entrée, une seule authentification
- **Type**: idea
- **Status**: blocked — waiting for Flavien
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: lecture du repo, revue de l'architecture

Trois fronts (PHP, Dash, Next) pour une seule application : Dash 11 233 lignes, PHP 9 720, Next
2 235. Flavien a une branche `refactor/nextJS_front` : décider avec lui la cible et le calendrier.

Proposition : Next remplace le PHP page par page, sans réécriture d'un coup, `mobility-admin.php`
en dernier. Les écrans de saisie de Dash passent à Next (T-37), les graphiques en lecture seule y
restent tant que rien ne pousse à les déplacer. Préalables : T-34, T-35, T-36.

### T-37 · Les écrans de saisie de Dash passent à Next
- **Type**: idea
- **Status**: blocked — waiting for T-12
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture

Recenser les vues Dash qui écrivent (`app5_module_enseignant_edit.py`, par exemple) et les migrer
une à une. Réécrire les graphiques en React coûterait cher pour peu de gain : ils restent en Dash.

### T-38 · Le RAG hors de l'image Dash
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture

`dashboards/apc_dash/polytech_rag/` embarque `sentence-transformers` et `faiss-cpu` dans l'image
de tous les tableaux de bord. Le sortir dans son propre conteneur, appelé par `apc20_chatbot`, en
respectant [AI-FEATURES].
