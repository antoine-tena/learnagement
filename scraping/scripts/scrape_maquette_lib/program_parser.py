"""Parsing de la maquette (parcours, UE, modules et contraintes) depuis la page formation."""

from __future__ import annotations

import copy
import logging
import re
import unicodedata
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

log = logging.getLogger("scrape_idu")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def to_number(tok: str):
    """'40,5h' -> 40.5 ; '8' -> 8 ; '-' -> None."""
    m = re.search(r"\d+(?:[.,]\d+)?", tok or "")
    if not m:
        return None
    v = float(m.group(0).replace(",", "."))
    return int(v) if v.is_integer() else v


def own_text(li: Tag) -> str:
    """Texte propre d'un <li> (sans sous-listes ni liens)."""
    clone = copy.copy(li)
    for sub in clone.find_all(["ul", "ol"]):
        sub.decompose()
    for a in clone.find_all("a"):
        a.decompose()
    return clone.get_text(" ", strip=True)


def parse_row(li: Tag | None) -> dict:
    """Ligne de maquette : 4 cellules positionnelles ECTS | CM | TD | TP ('-' si vide)."""
    out = {"ects": None, "cm": None, "td": None, "tp": None}
    if li is None:
        return out
    txt = re.sub(r"cr[ée]dits?", "", own_text(li), flags=re.I)
    toks = txt.split()
    if len(toks) == 4:
        out["ects"], out["cm"], out["td"], out["tp"] = (to_number(t) for t in toks)
    elif toks:
        out["_ligne_brute"] = txt  # structure inattendue : on garde le texte pour debug
    return out


def parse_constraint(txt: str) -> dict | None:
    t = norm(txt)
    if t.startswith("facultatif"):
        return {"type": "facultatif", "libelle": txt}
    m = re.search(r"au choix\s*:?\s*(\d+)\s*parmi\s*(\d+)", txt, flags=re.I)
    if m:
        return {
            "type": "choix",
            "a_choisir": int(m.group(1)),
            "parmi": int(m.group(2)),
            "libelle": txt,
        }
    if t.startswith("au choix"):
        return {"type": "choix", "libelle": txt}
    return None


def split_code(title: str) -> tuple[str | None, str]:
    """'UE704 Visualisation...' -> ('UE704', 'Visualisation...') ; 'Big Data (DATA831_IDU)' -> ('DATA831_IDU', 'Big Data')."""
    m = re.match(r"^(UE\d{3})\s+(.*)$", title)
    if m:
        return m.group(1), m.group(2).strip()
    m = re.search(r"\(\s*([A-Za-z0-9_]+)\s*\)\s*$", title)
    if m:
        return m.group(1), title[: m.start()].strip()
    return None, title.strip()


def semester_of(ue_code: str | None) -> int | None:
    """UE501 -> 5 ; UE001 (stage fin d'etudes) -> 10."""
    m = re.match(r"^UE(\d)\d{2}$", ue_code or "")
    if not m:
        return None
    d = int(m.group(1))
    return 10 if d == 0 else d


def contact_hours(n: dict) -> float | int | None:
    vals = [n[k] for k in ("cm", "td", "tp") if n.get(k) is not None]
    return sum(vals) if vals else None


def group_constraints(li: Tag | None) -> list[dict]:
    """Remonte les <li> 'Facultatif' / 'Au choix' (sans lien propre) qui encadrent un item."""
    out: list[dict] = []
    node = li.find_parent("li") if li else None
    while node is not None:
        first = node.find("a", href=True)
        if first is not None and first.find_parent("li") is node:
            break  # on est arrive au module/UE parent
        c = parse_constraint(own_text(node))
        if c:
            out.append(c)
        node = node.find_parent("li")
    return out


def parse_program(soup: BeautifulSoup, formation_url: str):
    base = formation_url[: -len(".html")] + "/"
    parcours: dict[str, dict] = {}
    nodes: dict[str, dict] = {}

    for a in soup.find_all("a", href=True):
        url = urljoin(formation_url, a["href"]).split("#")[0].split("?")[0]
        if not (url.startswith(base) and url.endswith(".html")):
            continue
        segs = url[len(base) : -len(".html")].split("/")
        title = a.get_text(" ", strip=True)
        if not title:
            continue

        if len(segs) == 1:  # page d'un parcours
            p = parcours.setdefault(segs[0], {"url": url, "nom": None})
            if p["nom"] is None and not norm(title).startswith("voir"):
                p["nom"] = title
            continue
        if url in nodes:
            continue

        li = a.find_parent("li")
        code, titre = split_code(title)
        node = {
            "type": "UE" if len(segs) == 2 else "module",
            "code": code,
            "titre": titre,
            "url": url,
            "_parcours": segs[0],
            "_depth": len(segs),
            "_parent": url.rsplit("/", 1)[0] + ".html",
            **parse_row(li),
            "contraintes": group_constraints(li),
        }
        nodes[url] = node

    # Hierarchie via le chemin d'URL
    ues: dict[str, list[dict]] = {k: [] for k in parcours}
    for n in nodes.values():
        parent = nodes.get(n["_parent"])
        if n["_depth"] == 2:
            ues.setdefault(n["_parcours"], []).append(n)
        elif parent is not None:
            parent.setdefault(
                "sous_modules" if parent["type"] == "module" else "modules", []
            ).append(n)
        else:
            log.warning("Parent introuvable pour %s", n["url"])
    return parcours, ues, nodes
