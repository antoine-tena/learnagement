# Architecture cible

Où va le repo. L'état actuel est décrit par le [README](../README.md) et la carte du
[CLAUDE.md](../CLAUDE.md) ; chaque étape ci-dessous a son ticket dans le
[backlog](backlog/backlog.md). Ce qui existe déjà est signalé comme tel ; le reste est à faire.

## Ce que le repo tient ensemble

1. **Un outil en production**, utilisé par les enseignants, les étudiants et les administratifs,
   avec des données personnelles.
2. **Un outil pour apprendre**, où des étudiants de tous niveaux, qui changent chaque année,
   essaient, se trompent et recommencent.
3. **Un seul mainteneur**, Flavien Vernier, qui relit les merges : chaque PR doit se relire vite.

D'où quatre principes :

- **Deux zones dès la racine** : `app/` tourne en production, `lab/` sert à apprendre. Rien de
  `lab/` n'entre dans une image de production.
- **Un seul cœur** : l'API est la seule à lire et écrire la base. C'est déjà vrai pour le web et les
  tableaux de bord (la base n'est que sur le réseau interne, et ni `web/` ni `dashboards/` ne
  contiennent de SQL) ; le scraping écrit encore directement en base.
- **Les mêmes noms partout** : un domaine est un dossier, qui porte le même nom dans chaque
  application, d'après le [glossaire](glossary.md).
- **La machine vérifie, l'humain juge** : tout ce qui se vérifie l'est avant la PR ; le relecteur
  ne regarde que ce qu'une machine ne sait pas juger.

## L'arborescence

```
learnagement/
├── README.md            commencer ici
├── CONTRIBUTING.md      lab ou app, ouvrir une PR, ce que la CI vérifie
├── Learnagement.py      la seule commande à connaître
│
├── app/                 EN PRODUCTION : utilisé par les profs et les étudiants
│   ├── portal/          la porte d'entrée : connexion CAS, routes, contrôle de session
│   ├── api/             Python · FastAPI : la seule partie qui touche la base
│   ├── web/             PHP : les pages principales
│   ├── dashboards/      Python · Dash : les tableaux de bord
│   ├── assistant/       Python : l'assistant APC (RAG)
│   └── importers/       Python : import des données externes (ADE, catalogue USMB)
│
├── lab/                 APPRENDRE : choisir un langage, rien ne part en production
│   ├── README.md        le tableau pour choisir
│   └── php/  python/  javascript/  java/  csharp/  go/  rust/
│
├── database/            migrations/, fake-data/ (données fictives), open-data/, tools/
├── deploy/              environnements, sauvegardes, certificats
├── launcher/            le code de Learnagement.py
├── docs/                guides, glossaire, décisions (adr/), backlog/
└── archive/             le code mort gardé pour mémoire
```

| Aujourd'hui | Demain |
|---|---|
| `backend/` | `app/api/` |
| `web/` | `app/web/` |
| `dashboards/` | `app/dashboards/` |
| `assistant/` (la recherche vectorielle de `polytech_rag`, T-38) | `app/assistant/` |
| `scraping/` | `app/importers/` |
| `frontend/` (Next, absent de la production) | `lab/javascript/nextjs/`, si T-12 le retient |
| `db/sql/`, `db/freeData/`, `db/tools/` | `database/migrations/`, `database/open-data/`, `database/tools/` |
| `docker/<conteneur>/` | `Containerfile` et `compose.yaml` dans le dossier de chaque application |
| `docker/compose/`, `config/` | `deploy/` |

Les déplacements gardent l'historique (`git mv`) et ne changent aucune des interfaces que les
étudiants utilisent (routes de l'API, variables d'environnement, commandes du lanceur) ; chaque
déplacement est annoncé dans le README.

## Le même rythme dans chaque application

Chaque application a un `README.md`, son `Containerfile`, son `compose.yaml`, un dossier `core/`
pour la mécanique commune, puis un dossier par domaine, avec ses tests à côté du code.

```
app/api/mobility/        app/web/mobility/           app/dashboards/mobility/
├── api.py               ├── admin/                  ├── staff.py
├── services.py          │   ├── view.php            ├── student.py
├── schemas.py           │   ├── actions.php         └── data.py
├── queries.py           │   ├── js/
└── tests/               │   └── style.css
                         └── map/
```

- **API** : `api.py` reçoit la requête et délègue (une route de 15 lignes au plus, [VIEW-15]),
  `services.py` porte les règles, `schemas.py` les entrées et les sorties, `queries.py` le SQL à
  paramètres liés.
- **Web** : une page est un dossier : `view.php` (ce qu'on affiche), `actions.php` (ce que les
  formulaires envoient), `js/`, `style.css`.
- **Tableaux de bord** : un fichier par rôle (`student.py`, `teacher.py`, `staff.py`) et
  `data.py` pour le chargement.
- **Couches vérifiées** : import-linter en Python (une route n'appelle que son service, un domaine
  ne lit pas les requêtes d'un autre), deptrac en PHP (une page ne touche jamais la base).

## La porte d'entrée (`app/portal/`, T-41)

- Un seul domaine, des chemins au lieu de ports : `/` pour le web, `/api/`, `/dashboards/`,
  `/assistant/`.
- La session CAS s'ouvre une fois, par l'API. Le proxy (Caddy) vérifie la session avant de servir
  une page et transmet le jeton de l'utilisateur ; le cookie est `__Host-`, `HttpOnly`, `Secure`,
  `SameSite=Lax` ([COOKIES]).
- Les pages des autres applications s'affichent dans le cadre du web (iframe), au lieu des
  redirections actuelles vers un autre port (`web/views/dashboard/python.php`).
- L'API revérifie les droits à chaque appel : une page, même mal écrite, ne montre jamais plus que
  ce que l'utilisateur a le droit de voir.
- Plus tard : un jeton limité à ce qu'une page déclare lire, et LTI 1.3 pour ouvrir une page dans
  la plateforme de cours.

## Le contrat de l'API

- `app/api/openapi.json` est exporté et versionné à chaque changement de l'API ([OPENAPI]).
- En CI, oasdiff bloque une PR qui casse une route, en entrée ou en sortie ; un changement
  incompatible ouvre `/api/v2/` ([FROZEN-CONTRACT]). Schemathesis vérifie que l'API respecte son
  contrat.
- OpenAPI Generator produit un client typé par langage, généré au lancement, jamais commité.
- La fabrique de routes (`backend/api/route_factory.py`) reste : une requête SQL décrite devient une
  route, ce qui est accessible aux débutants. Chaque requête déclare son schéma de réponse, pour
  que le contrat soit typé.

## Le lab (`lab/`, T-50)

`lab/README.md` commence par le tableau qui aide à choisir (durées visées) :

| Je veux… | Niveau | Dossier | Première page |
|---|---|---|---|
| le web côté serveur | débutant | `lab/php/vanilla/` | 30 min |
| Python et les données | débutant | `lab/python/flask/`, `lab/python/dash/` | 30 min |
| JavaScript sans framework | débutant | `lab/javascript/vanilla/` | 30 min |
| un framework front | intermédiaire | `lab/javascript/react/`, `vue/`, `svelte/`, `nextjs/` | 1 h |
| un back typé | intermédiaire | `lab/java/spring-boot/`, `csharp/aspnet/`, `go/net-http/`, `rust/axum/` | 2 h |

Chaque framework a le même kit, et la CI refuse un dossier qui n'en a pas :

```
lab/php/vanilla/
├── README.md       démarrer en 10 minutes
├── lab.toml        niveau, commandes pour installer, lancer, vérifier
├── example/        une page complète et commentée
├── template/       ce que copie `lab new`
└── projects/       un dossier par projet, nommé par ce qu'il fait
```

```
python Learnagement.py lab new php/vanilla mes-absences
python Learnagement.py lab run php/vanilla/projects/mes-absences
```

- Le lab tourne sur la vraie API et sur des données fictives (T-51) : jamais de données réelles.
- Un projet de back réimplémente une partie de l'API dans son langage ; la suite de tests du
  contrat prouve qu'il se comporte pareil.
- Les projets s'affichent sur l'instance de recette, jamais en production.
- Une page écrite dans un langage de production (PHP, Dash), qui respecte les règles, a ses tests,
  répond à un ticket et a un enseignant pour la parrainer, monte dans `app/` par une PR de
  déplacement.
- Un projet sans activité depuis un an part dans `archive/`, par une PR que la CI propose.

## Les règles, vérifiées par la machine (T-46)

| Langage | Mise en forme (corrigée seule) | Analyse | Couches |
|---|---|---|---|
| Python | ruff format | ruff, mypy strict | import-linter |
| PHP | PHP-CS-Fixer | PHPStan, niveau relevé pas à pas | deptrac |
| JS / TS | Prettier | ESLint, `tsc` strict | dependency-cruiser |
| Java · C# · Go · Rust (lab) | Spotless · dotnet format · gofmt · rustfmt | Checkstyle · analyseurs .NET · golangci-lint · clippy | |

- La charte couvre aussi le `.php` et le `.js` (taille des fichiers et des fonctions, noms) ; la
  dette actuelle est un plafond qui ne fait que baisser, la CI reste verte dès le premier jour.
- Les hooks de pré-commit s'installent au premier lancement et corrigent la mise en forme avant la
  PR.
- Le lab suit les mêmes règles que l'app : les apprendre fait partie de la pédagogie. La zone ne
  change que la personne qui approuve.

## Les relectures

| Zone | Qui approuve |
|---|---|
| `lab/` | les mentors : enseignants des cours, étudiants confirmés |
| `docs/` | un co-mainteneur |
| `app/`, `database/`, `deploy/`, `launcher/` | Flavien |

- Une PR touche une seule zone et reste courte.
- Une PR qui ne fait que déplacer des fichiers est étiquetée « déplacement pur » quand la CI l'a
  prouvé : elle s'approuve en une minute.
- La CI poste un seul commentaire par PR : zone, règles, tests, routes cassées ou non, migrations
  avec leur SQL, nouvelles dépendances, captures des pages modifiées sur données fictives.
- Une PR approuvée et verte se merge seule.
- La restructuration se prépare sur la branche `antoine-tena` du fork et sera proposée à `dev` en
  une PR, faite de commits atomiques dans l'ordre des phases, pour se relire commit par commit.

## Ce qui est réécrit, et ce qui est seulement découpé (T-49)

| Code | Ce qu'on fait |
|---|---|
| `web/views/dashboard/mobility-admin.php` (2 953 lignes, le JS dans la page) | découpé en dossier de page, JS réécrit en modules |
| `mobility-map.php` et `mobility-map_open.php` (31 lignes de différence) | fusionnés en une page paramétrée |
| `backend/domains/lnm_university.py` (2 155 lignes), `maquette_module.py` (1 249) | découpés en `mobility/` et `curriculum/` ; les routes de plus de 100 lignes réécrites, tests d'abord |
| SQL assemblé à la main (9 endroits) | paramètres liés |
| vieux code commenté, `test.php`, `app11_dag_dependance_new.py` | supprimés, l'historique git les garde |
| scraping qui écrit en base | passe par des routes d'import de l'API |

Le reste est déplacé tel quel, puis découpé et renommé sans changer ce qu'il fait.

## Une production prête pour la charge (T-52, T-39)

- API sans état, lancée en plusieurs copies derrière la porte d'entrée.
- Postgres, un schéma par domaine, SQLAlchemy et Alembic ([ORM], [MIGRATIONS]).
- Une file de tâches persistée pour les exports, les imports et l'assistant ([OUT-OF-REQUEST]).
- OpenTelemetry pour les traces et les métriques, le même standard dans tous les langages.
- Des images construites en CI, des sondes de santé, des sauvegardes testées (T-44).
- Compose sur un serveur aujourd'hui ; les mêmes images passent sur Kubernetes sans changer le code.

## Les étapes

| Phase | Ticket |
|---|---|
| Urgences | T-44 (sauvegardes), T-45 (phpMyAdmin) |
| A. Les règles vérifiées partout | T-46 |
| B. La nouvelle arborescence | T-47 |
| C. Découper et bien nommer | T-48 |
| D. Réécrire ce qui doit l'être | T-49 |
| E. Les nouveautés | T-41 (porte d'entrée), T-50 (lab), T-51 (données fictives), T-39 (Postgres), T-52 (production) |

## À décider avec Flavien

L'arborescence `app/` et `lab/` se fait sur le fork, puis se montre à Flavien, qui la reprend
ou non.

- Le sort de Next (T-12).
- Le glossaire, et ses points à confirmer.
- La délégation des relectures par zone.
- Où vont les sauvegardes : ce sont des données personnelles.
- phpMyAdmin : le retirer de la production, ou ne l'ouvrir que par un tunnel SSH (T-45).
- Postgres avec SQLAlchemy et Alembic, à la place des migrations SQL et des conventions de
  [db/README.md](db/README.md) (T-39).
- Les noms de branches : ceux de [git.md](git.md) ou ceux de la règle [BRANCHES] d'ion-repo.
