"""Enrichissement des nœuds et finalisation de l'arbre maquette."""

from __future__ import annotations

import logging

from .detail_parser import parse_detail
from .fetcher import Fetcher
from .program_parser import contact_hours

log = logging.getLogger("scrape_idu")


def enrich(node: dict, fetcher: Fetcher, keep_raw: bool) -> None:
    try:
        d = parse_detail(fetcher.get(node["url"]))
    except Exception as exc:  # noqa: BLE001
        node["erreur_detail"] = str(exc)
        log.error("Detail KO %s : %s", node["url"], exc)
        return
    if node.get("ects") is None and d.get("ects") is not None:
        node["ects"] = d["ects"]
    d.pop("titre_page", None)
    d.pop("ects", None)
    if not keep_raw:
        d.pop("texte_brut", None)
    node.update(d)


def finalize(node: dict) -> dict:
    node["heures"] = {
        "cm": node.pop("cm", None),
        "td": node.pop("td", None),
        "tp": node.pop("tp", None),
    }
    node["heures"]["contact_total"] = contact_hours(node["heures"])
    for k in ("_parcours", "_depth", "_parent"):
        node.pop(k, None)
    for child_key in ("modules", "sous_modules"):
        for ch in node.get(child_key, []):
            finalize(ch)
    return node


def walk(node: dict):
    yield node
    for k in ("modules", "sous_modules"):
        for ch in node.get(k, []):
            yield from walk(ch)
