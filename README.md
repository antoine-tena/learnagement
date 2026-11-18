# learnagement
Learnagement (Learning management) est un outil d'intégration de données de l'enseignement.
Il a pour but fonctionnel de faire le pont entre étudiants, enseignants et administratifs.
Il est principalement développé par les étudiants de l'USMB, ceux de la filière IDU de Polytech Annecy dans le cadre d'un apprentissage par projet et ceux de Licence de l'UFR SCEM dans le cadre de projets.

L'App Web s'organise autour de différents objectifs enrichis par les axes de développement choisi par les étudiants, enseignants et services administratifs : la gestion du planning prévisionnel des enseignants, la cohérence entre le MCCC, le prévisionnel et la planification réelle, la gestion des absences des étudiants...



## Prérequis
OS X, Unix or Windows,
[Podman](https://podman.io/docs/installation) et podman-compose (ou Docker),
Python 3.12 ou plus,
[uv](https://docs.astral.sh/uv/getting-started/installation/).

## Installation et lancement

### Dev Mode (Bootstrap)

Création de l'environnement, installation ou mise à jour des dépendances, lancement de l'app
```bash
python3 bootstrap.py
```
L'environnement sera créé dans /.venv. Le bootstrap installe aussi des hooks git (post-commit,
post-merge, post-rewrite) qui écrivent le commit courant dans `.env.git` (`GIT_COMMIT`).
Hors production, il installe aussi le hook de pré-commit (avec `uv tool install` : `pre-commit`
et `ion-repo`, qui fournit `charter`) : avant chaque commit, la mise en forme est corrigée et les
règles de `charter.toml` vérifiées sur les fichiers commités. Le PHP de `web/` se vérifie par
`web/tools/run.sh` (le PHP de la machine, sinon podman), son JavaScript par pnpm ;
`openapi.json`, à la racine, est le schéma de l'API, réécrit par
`cd backend && uv run python -m tools.export_openapi --output ../openapi.json`.

### Dev Mode (a la mano)

L'app se lance avec podman (`podman machine start` sous macOS et Windows) ; `uv run` prépare l'environnement :
```bash
uv run python Learnagement.py start
```

To configure your instance, edit specific ".env_XXX.env" files and restarts the app with:
```bash
uv run python Learnagement.py start --env XXX
```

Au lancement, le lanceur écrit `docker/compose.yaml` à partir des fragments de
`docker/compose/` (un par conteneur, Next seulement en dev), attend que chaque conteneur réponde à
sa sonde `/health`, puis arrête l'instance quand `podman compose up` se termine. Sans terminal
interactif, il refuse de demander les mots de passe.

**Changement d'interface (novembre 2026)** : le conteneur MySQL s'appelle désormais
`learnagement_data_mysql_<instance>`. Une instance existante corrige `MYSQL_SERVER` dans son `.env`
(ou régénère son environnement), et son `docker/compose.yaml` est réécrit à chaque lancement.

**Changement d'interface (novembre 2026)** : le lanceur appelle `podman` et `podman compose` par
défaut, et la compose écrite s'appelle `docker/compose.yaml` (avant : `docker-compose.yml`).
Pour garder docker, mettre `DOCKER_COMMAND=docker` et `DOCKER_COMPOSE_COMMAND="docker compose"`
dans le `.env` de l'instance. Les images se construisent depuis les `Containerfile` de `docker/`.

For any help
```bash
uv run python Learnagement.py --help
```

### Production Mode

Generate self certificate:
```bash
uv run python -m launcher.security
```

Generate environment
```bash
python bootstrap.py generate-env --env prod
```

Edit the .env file to configure your instance.

Run with prod environnement (secure):
```bash
uv run python Learnagement.py start --env prod
```
Note, containers will rebuild.


## Utilisation

Lors du 1e lancement il vous sera demandé si vous souhaitez charger des données. Hors production,
le lanceur propose un jeu fictif (`small`, `medium` ou `large`) : des promos, étudiants,
enseignants, stages, vœux de mobilité, séances et absences inventés, posés sur les maquettes
publiques de Polytech Annecy-Chambéry. Aucune personne réelle, tous les mails en `@example.org`.
Le même jeu se régénère à tout moment, identique pour une même graine :
```bash
python Learnagement.py fake-data --size medium --seed 2026
```
Il est écrit dans `db/data/`, que MySQL ne lit qu'à sa première initialisation.

Comptes de test du jeu fictif, tous avec le mot de passe `learnagement-fictif` ; le login est
le mail, comme pour tout compte interne :

| Identifiant | Profil | Rôle |
|---|---|---|
| `etudiant.demo@example.org` | étudiant | IDU 4e année |
| `enseignant.demo@example.org` | enseignant | sans rôle |
| `entreprises.demo@example.org` | enseignant | Relation entreprises |
| `etudes.demo@example.org` | administratif | Responsable études |
| `international.demo@example.org` | administratif | Relations internationales |
| `scolarite.demo@example.org` | administratif | Responsable de la scolarité |

Si vous avez chargé le jeu de données libres "small", vous trouverez via PhPMyAdmin un ensemble d'utilisateurs de test dont :
- un enseignant : AMELIE.CODRON@truc.com / toto
- un étudiant : LAURENT.BONNIFAIT@machin.com / toto
- un administratif : pierre.tartampion@truc.com / toto

Pour tous les utilisateurs - administratif, enseignant ou étudiant - qui ont un mot de passe, ce dernier est ```toto```.

Si vous n'avez pas chargé de données de test, vous devrez saisir ou importer vos propres données

**Multi-instances** :

Si vous souhaitez lancer plusieurs instances de Learnagement sur la même machine :
- Re-cloner le dépot GIT
- Re-faire la procédure de lancement initiale en changeant le nom et le numéro d'instance

Actuellement 4 instances en parallèle sont possibles.

## Changements d'interface

- **2026-11-18** : nouvelle variable `TRUSTED_PROXIES` (`config/env.skeleton`) : les proxys dont
  l'API croit l'en-tête `X-Forwarded-For`, par défaut les réseaux des conteneurs. La limite de
  débit de `/token` et de l'activation compte ainsi par client réel derrière le front PHP ; le
  front PHP transmet l'adresse du client. Le front Next ne la transmet pas encore.
- **2026-11-18** : nouvelle commande du lanceur, `fake-data`, et nouvelle question au premier
  lancement hors production : un jeu fictif (`small` par défaut) ou vos propres fichiers
  (`none`, l'ancien comportement). La production ne change pas.
- **2026-11-18** : la base refuse (erreur SQL 45000) une personne dont le login ou le mail existe
  déjà dans une autre des tables `LNM_administratif`, `LNM_enseignant`, `LNM_etudiant`
  (migration `V0.4.3`). Avant de l'appliquer, `db/tools/people_in_several_tables.sql` liste les
  doublons déjà présents, à régler à la main.
- **2026-11-18** : nouvelle commande `python Learnagement.py structuredb [--output FICHIER]` :
  la structure de la base sans ses données (tables avec leurs commentaires, vues, routines,
  triggers), par défaut dans `db/backup/structure.sql`.
- **2026-11-18** : un compte interne s'active par lien, plus en envoyant un hash à l'admin.
  `POST /account-activation` (`{"login"}`, administratif seulement) renvoie un jeton à usage
  unique valable 7 jours ; la personne ouvre `/activateAccount?token=<jeton>` sur le front Next,
  qui envoie le mot de passe à `POST /account-activation/confirm` (`{"token", "password"}`, 12
  caractères au moins) : l'API le hache. Migration `V0.4.2__account_activation.sql`.
- **2026-11-18** : phpMyAdmin ne démarre plus en production (`start --env prod`) : la base contient
  des données personnelles et son port était joignable depuis tout le VPN. Il reste en dev. Pour
  consulter la base de prod : `docker exec -it learnagement_data_mysql_<instance> mysql …` sur le
  serveur, ou une sauvegarde (`backupdb`).
- **2026-11-17** : `POST /modules/create` est retiré au profit de `POST /modules`. L'ancienne route
  écrivait dans des colonnes absentes de `MAQUETTE_module` (`nom_module`, `hProj`, `hPerso`) et
  échouait toujours. La nouvelle prend `code_module`, `nom`, `hCM`, `hTD`, `hTP`, `hProj`,
  `hPerso`, `ECTS`, `semestre`, `id_responsable`, `id_discipline`, réservée au responsable des
  études (409 si le code existe déjà). Nouvelle route : `GET /enseignants/{id}/rendus`, les
  rendus à venir d'un enseignant.

## Arrêt de l'app

L'app s'arrête, sans perte de donnée, via la commande :  
```bash
python Learnagement.py -stop
```

## Stop or Clean up from scratch the app


To destroy, remove all data to restart from scratch:  
```bash
python Learnagement.py stop
python Learnagement.py start --from_scratch
```

## Sauvegardes

En production, la base est sauvegardée chaque jour dans `db/backup/` par le conteneur
`data_mysql_backup` ; la vérification et la restauration sont décrites dans
[docs/prod.md](docs/prod.md#sauvegardes).

## Major upgrade

- step 1: back-up your DB
```bash
python Learnagement.py backupdb
```
- step 3: stop the current instance
```bash
python Learnagement.py stop
```
- step 4: deactivate your python environment
- step 4: move out of your Learnagement directory, get a new clone of Learnagement git, create, activate a new python environment and install requirements
- step 5: move into the new repository and switch to the required branch
- step 6: create "./db/data/" directory and copy your backed-up data into
```bash
mkdir ./db/data/
cp /[INITIAL PATH TO LEARNAGEMENT]/db/backup/VX.X.X__data_XXX[CURENT DATE].sql ./db/data/
```
- step 7: start the new instance (it will start like 1st time, so given the same port to the old instance to keep the service continuity)
```bash
python Learnagement.py start
```

[Doc](docs/README.md) - [Contribuer](CONTRIBUTING.md) - [Backlog](docs/backlog/backlog.md) - [CRediT](./CREDITS.md) - [Licence](./LICENSE)
