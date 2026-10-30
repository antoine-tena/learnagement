# Imports par scraping

Récupère des données depuis l'intranet de Polytech et les services de l'USMB, avec Chrome et le
compte de la personne qui lance la commande.

```bash
cd scraping
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

## Tests

```bash
uv run pytest
uv run mypy
uv run ruff check .
```

Les tests lisent de petites pages fictives et n'utilisent ni réseau, ni navigateur, ni base.
