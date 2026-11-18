# Imports par scraping

Récupère des données depuis l'intranet de Polytech et les services de l'USMB, avec Chrome et le
compte de la personne qui lance la commande.

```bash
cd app/importers
uv sync
uv run learnagement-scraping --help
uv run learnagement-scraping disciplines
```

| Commande | Ce qu'elle fait |
|---|---|
| `disciplines` | Enregistre les disciplines dans `MAQUETTE_discipline` |
| `semestres` | Enregistre les semestres dans `LNM_semestre` |
| `enseignants` | Crée les enseignants dans `LNM_enseignant` (service et décharge à 0, à compléter) |
| `etudiants` | Exporte le trombinoscope dans `out/` |
| `modules` | Exporte les fiches dans `out/` et met à jour les heures de `MAQUETTE_module` |
| `profil` | Exporte le profil de l'étudiant connecté dans `out/` |
| `notes` | Exporte son relevé de notes dans `out/` |
| `stages` | Exporte ses polypoints et ses stages dans `out/` |

Les commandes qui écrivent en base lisent `MYSQL_SERVER`, `MYSQL_PORT`, `MYSQL_DB`,
`MYSQL_USER_LOGIN` et `MYSQL_USER_PASSWORD` dans l'environnement ou un `.env`. Depuis la machine
hôte, `MYSQL_SERVER` doit désigner une adresse joignable.

`out/` contient des données personnelles : ce dossier est ignoré par git et ne doit pas être
partagé.

## Scripts autonomes

`scripts/` garde tels quels les scripts de l'équipe, hors du paquet et de ses règles (ruff, mypy),
pour que leurs auteurs puissent continuer à les faire évoluer. On les lance depuis `scripts/`, et
leurs sorties (emplois du temps, maquettes, cache) y restent, ignorées par git :

```bash
cd app/importers/scripts
uv run python scrape_maquette.py -o idu_maquette.json   # catalogue des formations USMB -> JSON
uv run python ical2json.py fetch <URL ADE ou fichier.ics> --filiere IDU   # -> snapshots/IDU/
```

`matching_26_27/` compare les heures de la maquette à l'emploi du temps ; ses graphiques demandent
matplotlib : `uv run --with matplotlib python matching_26_27/visu_barchart.py`.

## Tests

```bash
uv run pytest
uv run mypy
uv run ruff check .
```

Les tests lisent de petites pages fictives et n'utilisent ni réseau, ni navigateur, ni base.
