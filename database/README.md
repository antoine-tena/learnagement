# database

Le schéma MySQL et les données qui le remplissent au premier lancement.

| Dossier | Suivi par git | Contenu |
| --- | --- | --- |
| `migrations/` | oui | Le schéma, en scripts SQL versionnés. |
| `open-data/` | oui | Les jeux de données libres : formations publiques, petits jeux d'exemple, jeu de test ([Readme](open-data/Readme.md)). |
| `fake-data/` | oui | Le README du jeu fictif, généré par `python Learnagement.py fake-data` ([README](fake-data/README.md)). |
| `tools/` | oui | Scripts ponctuels d'import et d'entretien (ci-dessous). |
| `data/` | **non, privé** | Les données de départ de l'instance. Ne jamais publier. |
| `backup/` | **non, privé** | Les sauvegardes locales. Ne jamais publier. |
| `docker-entrypoint-initdb.d/` | non | Généré par le lanceur, lu par MySQL. |

## Comment la base naît

Au premier `python Learnagement.py start`, le lanceur (`launcher/db.py`) :

1. copie `migrations/` dans `docker-entrypoint-initdb.d/` ;
2. crée `data/` s'il manque et propose le jeu fictif (hors production) ;
3. lance `insertPrivateData.py`, qui lie les fichiers de `data/` dans `docker-entrypoint-initdb.d/` ;
4. démarre MySQL, qui exécute tout dans l'ordre des noms de fichiers, une seule fois.

Pour rejouer l'initialisation : `python Learnagement.py start --from_scratch` (irréversible,
instance arrêtée) ; un volume déjà rempli n'est jamais relu.

## Les migrations

- Nom : `V<majeur>.<mineur>.<correctif>__<sujet>.sql`, exécutés dans l'ordre du nom.
- Une migration publiée ne change plus : on corrige par une nouvelle.
- Un commit de migration ne mélange jamais schéma et logique métier.
- Les tables gardent leur préfixe et leur casse (`LNM_`, `MAQUETTE_`, `APC_`, `MOB_`…) ; leur sens
  est dans le [glossaire](../docs/glossary.md).
- `V0.99.0__trigger_init.sql` passe après toutes les autres : les triggers en dernier.

Le passage à Postgres, SQLAlchemy et Alembic est à l'étude (learnagement#T-39).

## `tools/`

| Fichier | Rôle |
| --- | --- |
| `ade2sql.py` | Les séances d'un export ADE vers la base. |
| `mobilitymap2sql.py` | Le CSV des universités partenaires vers un SQL de `open-data/`. |
| `createDB.py`, `config.skeleton` | Créer une base hors conteneur (copier `config.skeleton` en `config.py`). |
| `dumpDB.sh` | Un export ponctuel de la base. |
| `people_in_several_tables.sql` | Les personnes présentes dans plusieurs tables, sans données personnelles affichées. |

La sauvegarde quotidienne de la prod n'est pas ici : [deploy/backup/](../deploy/README.md).
