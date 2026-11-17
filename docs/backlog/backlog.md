# Backlog

Tout ce qui reste à faire sur Learnagement, en une seule liste ordonnée par priorité. Commencé
le **2026-10-30**. Comment écrire un ticket : [README.md](README.md) ; les tickets fermés sont
dans [done.md](done.md), ce qui a été écarté dans [rejected.md](rejected.md). **Rien d'autre
n'est ouvert.**

North star: **Learnagement in service**.

**Next free: T-53.**

---

## 🔴 Critical

### T-44 · Les sauvegardes automatiques, et une restauration testée
- **Type**: bug
- **Status**: blocked — waiting for Flavien (où vont les copies)
- **Opened**: 2026-11-17
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: lecture du code, 2026-11-17

La base de production, qui porte les stages et bientôt la mobilité d'environ 400 étudiants, est
sauvegardée chaque jour par le conteneur `data_mysql_backup` (`docker/backup/backup.sh`), et sa
restauration est essayée (`docs/prod.md`). Les copies restent sur le même serveur que la base,
et un échec ne prévient encore personne hors du serveur : deux décisions de Flavien
(`urgent.md`).

- [x] Écrire `backup.sh` : une sauvegarde par jour, une durée de conservation
- [ ] Une copie hors du serveur, dans un stockage que l'université accepte pour des données
  personnelles (décision dans `urgent.md`)
- [x] Restaurer une sauvegarde sur une instance de test, et décrire la marche à suivre dans
  `docs/prod.md`
- [x] Une alerte quand une sauvegarde échoue : sonde `unhealthy` et `BACKUP_ALERT_URL`
- [ ] Choisir où va l'alerte (mail, messagerie de l'équipe) et remplir `BACKUP_ALERT_URL`

## 🟠 Important

### T-45 · phpMyAdmin hors de la production
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: lecture du code, 2026-11-17

Le lanceur démarre phpMyAdmin en production (`launcher/config.py`, liste `prod`), sur un port
publié de l'hôte (`docker/compose/phpmyadmin.yml`) : une interface d'administration directe d'une
base qui contient des données personnelles, joignable depuis tout le VPN. Le retirer de la liste
`prod` ou, si Flavien en a besoin, ne l'ouvrir qu'en local par un tunnel SSH. Signaler le
changement dans le README.

### T-46 · Phase A : les règles vérifiées partout
- **Type**: improvement
- **Status**: in progress
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Avant de déplacer quoi que ce soit, la machine vérifie les règles dans tous les langages, pour que
les phases suivantes se relisent vite. Rien n'est déplacé ici.

- [x] La charte compte aussi le `.php` et le `.js` ([FILE-SIZE]), budget au niveau actuel (6)
- [x] ruff (lint et mise en forme) et mypy sur `dashboards/`, dans le pre-commit et la CI ; la
  dette, règle par règle et module par module, dans `dashboards/pyproject.toml`
- [ ] PHP-CS-Fixer et PHPStan sur `web/`, au niveau qui passe aujourd'hui, relevé ensuite
- [ ] Prettier et ESLint sur le JS de `web/`
- [ ] Les couches vérifiées : import-linter en Python, deptrac en PHP
- [ ] `openapi.json` exporté et versionné, vérifié en CI (le workflow `api-contract.yml`
  d'ion-repo, avec une commande d'export FastAPI) ; les routes cassées détectées (oasdiff), à
  proposer à ion-repo s'il ne le fait pas ([REPORT-TO-KILN])
- [x] Les hooks de pré-commit installés par `bootstrap.py`
- [ ] `no-commit-to-branch` protège `main` et `develop`, qui n'existe pas ici, mais ni `dev` ni
  `prerelease` : défaut d'un fichier généré, à corriger dans ion-repo ([REPORT-TO-KILN])
- [ ] La CI poste un commentaire par PR : règles, tests, routes cassées ou non, migrations,
  nouvelles dépendances

### T-47 · Phase B : la nouvelle arborescence
- **Type**: improvement
- **Status**: blocked — waiting for T-46
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Les dossiers prennent leur place cible (`app/`, `lab/`, `database/`, `deploy/`) par déplacements
purs (`git mv`) : une application par commit, sans changer ce que fait le code. L'arborescence se
fait valider par Flavien (`urgent.md`) : refusée, elle coûterait toute la phase.

- [ ] `backend/` → `app/api/`, `web/` → `app/web/`, `dashboards/` → `app/dashboards/`,
  `scraping/` → `app/importers/`
- [ ] `db/` → `database/` (`migrations/`, `open-data/`, `tools/`)
- [ ] `Containerfile` et `compose.yaml` dans le dossier de chaque application ;
  `docker/compose/` et `config/` → `deploy/`
- [ ] `frontend/` → `lab/javascript/nextjs/`, si T-12 le retient
- [ ] Le lanceur, la CI, le pre-commit et `charter.toml` suivent les nouveaux chemins
- [ ] `docs/moved.md` : chaque ancien chemin et le nouveau, pour les branches en cours
- [ ] README, `CONTRIBUTING.md`, carte du `CLAUDE.md` à jour ; CODEOWNERS par zone
- [ ] Prévenir les contributeurs avant (T-33)

### T-38 · Le RAG hors de l'image Dash
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture ; priorité relevée le 2026-11-17 (serveur déjà surchargé)

`dashboards/apc_dash/polytech_rag/` embarque `sentence-transformers` et `faiss-cpu` dans l'image
de tous les tableaux de bord. Le sortir dans son propre conteneur, appelé par `apc20_chatbot`, en
respectant [AI-FEATURES].

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
- **Status**: in progress — fix/front-auth-secrets
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: @antoine-tena · **Due**: —
- **Origin**: revue de l'architecture

Le jeton ne passe plus par l'URL : le PHP pose un cookie `lnm_token` (`HttpOnly`, `SameSite=Strict`,
`Secure` en HTTPS), que Dash lit sur le même hôte ; Next ne lisait pas `?jwt_token` et ne le reçoit
plus. `nextjs.php` force encore `http`, mais seule la connexion de Next y transite désormais.

- [ ] Vérifier sur une instance lancée, en HTTP puis en HTTPS : connexion, passage du PHP à Dash,
  navigation entre les pages de Dash, déconnexion (code modifié, pas encore lancé).
- [x] Transmettre l'authentification autrement : cookie `HttpOnly` et `Secure` sur un même domaine.
- [ ] Servir Next en HTTPS.

### T-19 · Zod 4 et audit des dépendances du front
- **Type**: bug
- **Status**: todo
- **Opened**: 2026-10-30
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: `pnpm audit` après T-14

`pnpm audit` signale encore zod < 4.6.6 (élevée, dépendance directe en 3.x, version majeure à
passer), postcss-selector-parser par `@tailwindcss/typography` (modérée) et deepmerge par
`@svgr/webpack` (faible, sans correctif).

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

### T-48 · Phase C : découper et bien nommer, domaine par domaine
- **Type**: improvement
- **Status**: blocked — waiting for T-47
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Chaque application prend le même rythme : `core/`, puis un dossier par domaine du glossaire
(`docs/glossary.md`). Un domaine par série de commits : on découpe et on renomme sans changer le
comportement, les tests passent avant et après. Regroupe T-11, T-29, T-31, T-27 et T-21.

- [ ] API : un paquet par domaine (`api.py`, `services.py`, `schemas.py`, `queries.py`,
  `tests/`) ; `core/` pour la configuration, la base, l'authentification et les droits
- [ ] Web : une page par dossier (`view.php`, `actions.php`, `js/`, `style.css`), rangée par domaine
- [ ] Tableaux de bord : un dossier par domaine, un fichier par rôle, sans préfixe `appNN_`
- [ ] Les noms du glossaire appliqués au code, sans toucher aux tables ni aux routes publiées
- [ ] La fabrique de routes déclare un schéma de réponse par requête

### T-49 · Phase D : réécrire le code qui doit l'être
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`), lecture du code, 2026-11-17

Seulement ce que le découpage ne suffit pas à rendre lisible : des tests qui figent le comportement
actuel d'abord, puis la réécriture. Le plus simple après T-48 ; le SQL et le code mort peuvent
partir avant.

- [ ] `mobility-admin.php` (2 953 lignes) : le JS en modules (indicateurs, tableau, filtres, exports)
- [ ] `mobility-map.php` et `mobility-map_open.php` (31 lignes de différence) : une seule page
- [ ] Les routes de plus de 100 lignes de la mobilité et des maquettes : route, service, requêtes
- [ ] Le SQL assemblé à la main (9 endroits, dont `lnm_university.py`, `lnm_calendar.py`,
  `init.py`) : des paramètres liés ([ORM])
- [ ] Le vieux code commenté (`api/dependencies.py`, `auth/authenticate_cas.py`…),
  `views/dashboard/test.php` et `app11_dag_dependance_new.py` : supprimés
- [ ] Le scraping n'écrit plus en base : il passe par des routes d'import de l'API

### T-51 · Des données fictives pour travailler
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

Le développement, la recette, la CI, le lab et les sessions Claude tournent sur des données
inventées, jamais réelles ([PERSONAL-DATA], [AI-CONFIDENTIALITY]). Les jeux de `db/freeData/` sont
figés ; un générateur produit des promos, des étudiants, des enseignants, des stages, des vœux de
mobilité et des absences cohérents, sur les maquettes publiques.

- [ ] Un générateur reproductible (graine fixe), en plusieurs tailles
- [ ] Le lanceur le propose au premier lancement, à côté des jeux libres
- [ ] Des comptes de test par rôle, listés dans le README

### T-50 · Le lab : apprendre dans le langage de son choix
- **Type**: idea
- **Status**: blocked — waiting for T-47, T-51
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`)

`lab/` à la racine : un dossier par langage puis par framework, chacun avec le même kit
(`README.md`, `lab.toml`, `example/`, `template/`, `projects/`). Rien n'en part en production ; le
détail est dans `docs/architecture.md`.

- [ ] `lab/README.md` : le tableau pour choisir (langage, niveau, ce qu'on apprend, durée visée)
- [ ] Le kit des premiers frameworks : `php/vanilla`, `python/flask`, `python/dash`,
  `javascript/vanilla`, `javascript/react`, `javascript/nextjs`, `java/spring-boot`
- [ ] `python Learnagement.py lab new` et `lab run`, qui lisent `lab.toml`
- [ ] Un client de l'API généré par langage (OpenAPI Generator), jamais commité
- [ ] La suite de tests du contrat (Schemathesis) pour les projets de back
- [ ] La CI refuse un dossier sans kit et vérifie chaque projet avec les outils de son langage
- [ ] L'instance de recette affiche les projets du lab
- [ ] Les règles de passage en production et d'archivage, dans `lab/README.md`

### T-52 · Une production prête pour la charge
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: architecture cible (`docs/architecture.md`), lecture du code, 2026-11-17

Le serveur sature déjà, selon Flavien. Le code montre des suspects : Dash lancé avec 2 processus
qui chargent chacun PyTorch par le RAG (T-38), l'API qui relance sa suite de tests et `uv sync` à
chaque démarrage, production comprise (`docker/backend/entrypoint.sh`), le code monté en volume
dans les conteneurs.

- [ ] Mesurer la mémoire et le processeur de chaque conteneur
- [ ] Des images construites en CI ; plus de tests ni d'installation au démarrage
- [ ] Une API sans état, lancée en plusieurs copies derrière la porte d'entrée (T-41)
- [ ] Une file de tâches persistée pour les exports Excel, les imports et l'assistant
  ([OUT-OF-REQUEST])
- [ ] OpenTelemetry pour les traces et les métriques, journaux structurés (T-13)
- [ ] Une limite de mémoire par conteneur, des sondes de santé (T-06)

### T-39 · La base passe de MySQL à Postgres
- **Type**: improvement
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17 ; architecture cible (`docs/architecture.md`)

Flavien veut passer à Postgres : un schéma par domaine (`docs/glossary.md`), la protection des
données personnelles ligne par ligne, des copies en lecture si la charge l'exige, et le moment de
renommer les tables. Ce qui sature le serveur aujourd'hui se mesure d'abord (T-52). Remplace T-26
(mise à jour de MySQL).

- [ ] Un schéma Postgres par domaine, les tables renommées d'après le glossaire
- [ ] SQLAlchemy et Alembic à la place des migrations `VX.Y.Z__*.sql` ([ORM], [MIGRATIONS]), à
  décider avec Flavien : ses conventions de base (`docs/db/README.md`) changent
- [ ] Migrer les données (pgloader), sur une copie d'abord
- [ ] Adapter le lanceur (`launcher/db.py` : initialisation, sauvegardes) et les fragments compose
- [ ] Coordonner avec les étudiants qui travaillent sur le déploiement automatique
- [ ] Signaler le changement dans le README (variables d'environnement, commandes du lanceur)

### T-40 · Le conteneur Next redémarre
- **Type**: bug
- **Status**: to verify — `frontend/`, `docker/frontend/`
- **Opened**: 2026-11-17
- **Effort**: S · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17

Selon Flavien, le front Next ne démarre plus depuis une montée de version ; il ne sert qu'au
développement et ne va pas en production. À réparer avant T-36, T-20, T-09 et T-19, qui n'ont de
sens que sur un front qui tourne.

Si T-12 retient la porte d'entrée, Next part dans le lab (T-47) et se répare là.
### T-43 · Le proxy CAS seulement en développement
- **Type**: task
- **Status**: to verify — `backend/auth/`, `config/`
- **Opened**: 2026-11-17
- **Effort**: XS · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17

L'université a autorisé l'application sur son CAS : le proxy qui passait par le site de
l'université n'est plus utilisé en production. Vérifier qu'il est désactivé dans `config/env.prod`
(ou l'équivalent) et le documenter comme outil de développement.

### T-36 · Les appels de Next visent des routes qui existent
- **Type**: bug
- **Status**: blocked — waiting for T-40
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

Fait partie des phases C et D (T-48, T-49).
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

Fait partie de la phase C (T-48).
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

Le glossaire (`docs/glossary.md`) fixe le nom de chaque mot du métier ; fait partie de la
phase C (T-48).
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

### T-27 · Nommage et structure des tableaux de bord
- **Type**: improvement
- **Status**: to verify — `dashboards/`
- **Opened**: 2026-10-30
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: ancien `ToDo/visualisation/ToDo.md`

L'ancienne liste demandait de revoir le nommage : vérifier ce qu'il reste après T-04.

Fait partie de la phase C (T-48).
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

Proposition (`docs/architecture.md`) : aucun front ne remplace les autres. Une porte d'entrée
(T-41) les réunit sous un domaine et une session ; le PHP et Dash restent en production ; Next,
absent de la production, part dans le lab (`lab/javascript/nextjs/`), d'où ses pages pourront
monter une à une. L'ancienne proposition (Next remplace le PHP page par page, T-37) reste possible
si Flavien la préfère.

### T-37 · Les écrans de saisie de Dash passent à Next
- **Type**: idea
- **Status**: blocked — waiting for T-12
- **Opened**: 2026-10-30
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: revue de l'architecture

Recenser les vues Dash qui écrivent (`app5_module_enseignant_edit.py`, par exemple) et les migrer
une à une. Réécrire les graphiques en React coûterait cher pour peu de gain : ils restent en Dash.

Inutile si T-12 retient la porte d'entrée (T-41) : les écrans de saisie restent en Dash.
### T-41 · La porte d'entrée : un domaine, une session, toutes les pages
- **Type**: idea
- **Status**: blocked — waiting for T-12
- **Opened**: 2026-11-17
- **Effort**: L · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17 ; architecture cible (`docs/architecture.md`)

Idée de Flavien : un seul front, où chacun contribue dans son langage. La cible la réalise en deux
parties : la porte d'entrée, ici, et le lab (T-50). Aujourd'hui, le PHP redirige vers Dash et Next
sur un autre port en posant un cookie (`web/views/dashboard/python.php`).

- [ ] Un proxy (Caddy) : un seul domaine, des chemins au lieu de ports (`/`, `/api/`,
  `/dashboards/`, `/assistant/`)
- [ ] La session CAS ouverte une fois, par l'API ; le proxy la vérifie avant de servir une page et
  transmet le jeton de l'utilisateur ([COOKIES])
- [ ] Les pages de Dash, puis celles du lab passées en production, affichées dans le cadre du web
- [ ] L'API revérifie les droits à chaque appel
- [ ] Plus tard : un jeton limité à ce qu'une page déclare lire, et LTI 1.3
### T-42 · Des projets extérieurs lisent les données par l'API
- **Type**: idea
- **Status**: todo
- **Opened**: 2026-11-17
- **Effort**: M · **Owner**: — · **Due**: —
- **Origin**: réunion avec Flavien Vernier, 2026-11-17

Des projets de recherche voisins (visualisation des maquettes et des compétences) veulent les
données de Learnagement. L'API n'est joignable que par le VPN de l'université.

- [ ] Décider : le projet tourne dans le même environnement, ou appelle l'API de l'extérieur
- [ ] Un accès en lecture seule, par jeton de service, sur les routes de maquettes et de modules
- [ ] Documenter ces routes (OpenAPI) comme un contrat stable
