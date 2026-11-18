# deploy

Ce qu'il faut pour assembler et faire tourner une instance, à part le code des applications.
Le lanceur lit ce dossier ; on n'y lance rien à la main.

| Chemin | Rôle |
| --- | --- |
| `env.skeleton` | Le modèle de `.env` : chaque variable, commentée, avec sa valeur par défaut. |
| `env.dev`, `env.prod` | Les valeurs propres à chaque environnement, posées sur le squelette. |
| `compose/` | Les fragments compose des services sans application (ci-dessous). |
| `backup/backup.sh` | La sauvegarde quotidienne de la base, dans le conteneur `data_mysql_backup`. |
| `phpmyadmin/` | La configuration de phpMyAdmin. |
| `certs/` | Ignoré : les certificats de `python -m launcher.security`. |
| `compose.yaml` | Ignoré : le fichier assemblé par le lanceur. |

## Les `.env`

`python Learnagement.py generate-env` produit le `.env` de la racine depuis `env.skeleton`, les
réponses de l'utilisateur et `env.<env>`, puis le recopie dans chaque conteneur. Une nouvelle
variable s'ajoute dans `env.skeleton` (et `env.dev`/`env.prod` si sa valeur change selon
l'environnement), jamais dans un `.env` généré. Renommer une variable casse les instances des
autres : on le signale dans le [README](../README.md).

## `compose/`

Le lanceur colle `_head.yml`, les fragments des services de l'environnement (ceux de
`app/*/compose.yaml` et ceux d'ici), puis `_tail.yml` (réseaux, volumes). Les chemins y sont
relatifs à `deploy/`.

| Fragment | Service |
| --- | --- |
| `data_mysql.yml` | MySQL 8.4, sur le réseau interne seulement, jamais de port ouvert. |
| `data_mysql_backup.yml` | La sauvegarde quotidienne (`backup/backup.sh`). |
| `phpmyadmin.yml` | phpMyAdmin (son sort en production : learnagement#T-45). |
| `etl.yml` | Un essai de Mage AI, dans aucun environnement tant qu'il n'est pas configuré. |

## La sauvegarde

`backup.sh` fait une sauvegarde par jour à `BACKUP_AT`, cohérente et compressée, garde
`BACKUP_RETENTION_DAYS` jours, et sa sonde de santé échoue si la dernière a raté ou date de plus de
`BACKUP_MAX_AGE_HOURS`. `backup.sh once` en fait une tout de suite. Les fichiers contiennent des
données personnelles : on les traite comme telles.

Mise en production : [docs/prod.md](../docs/prod.md).
