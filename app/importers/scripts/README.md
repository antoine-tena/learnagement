# scripts

Les scripts autonomes de l'équipe, gardés tels quels, hors du paquet `learnagement_scraping` et de
ses règles (ruff, mypy) pour que leurs auteurs continuent à les faire évoluer. Ils n'écrivent pas en
base : ils produisent des fichiers JSON, ignorés par git, dans ce dossier. On les lance d'ici :

```bash
cd app/importers/scripts
uv run python ical2json.py fetch <URL ADE ou fichier.ics> --filiere IDU
uv run python scrape_maquette.py -o idu_maquette.json
```

## Les trois outils

| Outil | Entrée | Sortie |
| --- | --- | --- |
| `ical2json.py` + `ical2json_lib/` | Un emploi du temps ADE (iCal, URL ou fichier). | `snapshots/<FILIERE>/<horodatage>/` : l'iCal brut, `edt.json`, l'historique des parsings ; les imports refusés dans `snapshots/_rejets/`. `reparse` relit les iCal déjà pris avec un parseur corrigé. |
| `scrape_maquette.py` + `scrape_maquette_lib/` | Le catalogue des formations USMB (Ametys / ODF) ; par défaut le diplôme IDU. | Un arbre JSON formation → parcours → semestres → UE → modules, avec ECTS, heures CM/TD/TP et le détail de chaque fiche. Cache disque et débit limité (`fetcher.py`). |
| `matching_26_27/` | Les JSON des deux outils ci-dessus, copiés à la main dans le dossier. | Des graphiques qui comparent les heures de la maquette à l'emploi du temps (demande matplotlib : `uv run --with matplotlib python matching_26_27/visu_barchart.py`). |

`python ical2json.py --help` et `python scrape_maquette.py --help` donnent toutes les options ; les
usages en tête de fichier citent encore leurs anciens noms (`edt_snapshots.py`, `scrape_idu.py`).

## Vers le paquet

Un script qui sert régulièrement et doit écrire en base passe dans le paquet
(`src/learnagement_scraping/`), avec tests et typage, puis passe par l'API plutôt que par la base
directement ([docs/architecture.md](../../../docs/architecture.md)).
