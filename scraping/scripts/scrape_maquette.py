#!/usr/bin/env python3
"""
Scraper du catalogue des formations USMB (Ametys / ODF) -> JSON.

Cible par defaut : Diplome ingenieur Informatique, Donnees, Usages (Polytech Annecy).

Structure produite :
  formation -> parcours[] -> semestres[] -> ue[] -> modules[] -> sous_modules[]
avec, pour chaque noeud : code, titre, url, ECTS, heures CM/TD/TP (+ total contact),
contraintes (facultatif / "au choix : 1 parmi N") et le detail de la page du cours
(presentation, objectifs, prerequis, plan du cours, competences, ... + toutes les
sections trouvees dans `sections`).

Dependances : pip install requests beautifulsoup4
Usage       : python scrape_idu.py -o idu.json
              python scrape_idu.py -o idu.json --parcours alternance --workers 4
              python scrape_idu.py --no-details -o maquette_seule.json
"""
from __future__ import annotations

import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from scrape_maquette_lib import (
    Fetcher,
    enrich,
    finalize,
    norm,
    parse_detail,
    parse_program,
    semester_of,
    walk,
)

DEFAULT_URL = (
    "https://formations.univ-smb.fr/fr/catalogue/cycle-preparatoire-et-diplome-d-ingenieur-FI/"
    "diplome-ingenieur-informatique-donnees-usages-M1JEXJEN.html"
)

log = logging.getLogger("scrape_idu")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("-o", "--out", default="idu_maquette.json")
    ap.add_argument(
        "--cache",
        default=".cache_formations",
        help="dossier de cache HTML (relancer = quasi instantane)",
    )
    ap.add_argument(
        "--no-details", action="store_true", help="maquette seule, sans visiter les pages UE/modules"
    )
    ap.add_argument(
        "--no-raw", action="store_true", help="ne pas inclure `texte_brut` des pages de detail"
    )
    ap.add_argument(
        "--parcours",
        help="ne garder que les parcours dont le nom/slug contient ce texte (ex: alternance)",
    )
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--delay", type=float, default=0.3, help="delai mini entre requetes (s)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s"
    )

    fetcher = Fetcher(Path(args.cache), delay=args.delay)
    html = fetcher.get(args.url)
    soup = BeautifulSoup(html, "html.parser")

    formation = parse_detail(html, drop_link_heavy_sections=True)
    formation.pop("texte_brut", None)
    parcours, ues, nodes = parse_program(soup, args.url)
    log.info("%d parcours, %d noeuds (UE + modules)", len(parcours), len(nodes))

    selected = {
        slug: p
        for slug, p in parcours.items()
        if not args.parcours or norm(args.parcours) in norm((p["nom"] or "") + " " + slug)
    }
    targets = [n for slug in selected for ue in ues.get(slug, []) for n in walk(ue)]

    if not args.no_details:
        log.info("Telechargement du detail de %d pages...", len(targets))
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            list(ex.map(lambda n: enrich(n, fetcher, not args.no_raw), targets))

    result_parcours = []
    for slug, p in selected.items():
        sems: dict[int | None, list[dict]] = {}
        for ue in ues.get(slug, []):
            sems.setdefault(semester_of(ue["code"]), []).append(finalize(ue))
        semestres = []
        for num in sorted(sems, key=lambda x: (x is None, x)):
            semestres.append(
                {
                    "numero": num,
                    "ects": sum(u["ects"] or 0 for u in sems[num]),
                    "ue": sems[num],
                }
            )
        result_parcours.append({"nom": p["nom"] or slug, "url": p["url"], "semestres": semestres})

    data = {
        "source": args.url,
        "extrait_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "formation": formation,
        "parcours": result_parcours,
    }
    Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    n_mod = sum(1 for n in targets if n["type"] == "module")
    log.info("OK -> %s (%d UE, %d modules)", args.out, len(targets) - n_mod, n_mod)


if __name__ == "__main__":
    main()
