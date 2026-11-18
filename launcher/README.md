# launcher

Le code de `Learnagement.py`, la seule commande à connaître pour faire tourner une instance :

```bash
python bootstrap.py            # premier lancement : uv, hooks de pré-commit, puis le lanceur
python Learnagement.py --help  # la liste des commandes
python Learnagement.py start   # démarre l'instance (--env dev|prod, --from_scratch pour repartir de zéro)
```

## Les modules

| Fichier | Rôle |
| --- | --- |
| `cli.py` | Les commandes click (`start`, `stop`, `generate-env`, `backupdb`, `structuredb`, `exportinstance`, `import-instance`, `fake-data`, `gui`). |
| `instance.py` | L'instance entière : changer d'environnement, repartir de zéro, exporter, importer. |
| `env.py` | Génère `.env` depuis `deploy/env.skeleton` et `deploy/env.<env>`, puis le recopie dans chaque conteneur. |
| `compose.py` | Assemble `deploy/compose.yaml` depuis les fragments, attend les sondes de santé. |
| `docker.py` | Les appels à podman et compose (`DOCKER_COMMAND`, `DOCKER_COMPOSE_COMMAND`). |
| `db.py` | La base : fichiers d'initialisation, compte administrateur, sauvegardes. |
| `config.py` | Les conteneurs de chaque environnement. |
| `git.py` | Écrit le commit courant dans `.env.git`, tenu à jour par des hooks git. |
| `dev_hooks.py` | Pose les hooks de pré-commit du poste de développement (jamais en prod). |
| `security.py` | Les certificats auto-signés : `python -m launcher.security`. |
| `tools.py` | Petits utilitaires (terminal). |
| `fake_data/` | Le générateur de données fictives (ci-dessous). |
| `backups/` | Ancienne sauvegarde planifiée en Python, pas branchée : la prod utilise `deploy/backup/`. |
| `tests/` | Les tests pytest du lanceur. |

## `fake_data/`

`python Learnagement.py fake-data` écrit un fichier SQL fictif, reproductible (même taille et même
graine, même fichier), posé sur le jeu public `database/open-data/Polytech_Annecy_Chambery/`. Il
est proposé au premier lancement hors production. Aucun nom de `vocabulary.py` ne désigne une
personne réelle ; les comptes de test (un par rôle) sont listés dans le
[README](../README.md), le jeu dans [database/fake-data/](../database/fake-data/README.md).

## Les règles

- On n'édite jamais un `.env` à la main dans un sous-dossier : on change `deploy/env.*` et on relance.
- Une commande du lanceur est une interface : la renommer se signale dans le [README](../README.md).
- Les tests : `uv run pytest launcher/tests` depuis la racine.
