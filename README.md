# learnagement
Learnagement (Learning management) est un outil d'intégration de données de l'enseignement.
Il a pour but fonctionnel de faire le pont entre étudiants, enseignants et administratifs.
Il est principalement développé par les étudiants de l'USMB, ceux de la filière IDU de Polytech Annecy dans le cadre d'un apprentissage par projet et ceux de Licence de l'UFR SCEM dans le cadre de projets.

L'App Web s'organise autour de différents objectifs enrichis par les axes de développement choisi par les étudiants, enseignants et services administratifs : la gestion du planning prévisionnel des enseignants, la cohérence entre le MCCC, le prévisionnel et la planification réelle, la gestion des absences des étudiants...



## Prérequis
OS X, Unix or Windows,
Docker desktop,
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

### Dev Mode (a la mano)

L'app se lance avec docker (pensez à lancer docker-desktop) ; `uv run` prépare l'environnement :
```bash
uv run python Learnagement.py start
```

To configure your instance, edit specific ".env_XXX.env" files and restarts the app with:
```bash
uv run python Learnagement.py start --env XXX
```

Au lancement, le lanceur écrit `docker/docker-compose.yml` à partir des fragments de
`docker/compose/` (un par conteneur, Next seulement en dev), attend que chaque conteneur réponde à
sa sonde `/health`, puis arrête l'instance quand `docker compose up` se termine. Sans terminal
interactif, il refuse de demander les mots de passe.

**Changement d'interface (novembre 2026)** : le conteneur MySQL s'appelle désormais
`learnagement_data_mysql_<instance>`. Une instance existante corrige `MYSQL_SERVER` dans son `.env`
(ou régénère son environnement), et son `docker/docker-compose.yml` est réécrit à chaque lancement.

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

Lors du 1e lancement il vous sera demandé si vous souhaitez charger des données.
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
