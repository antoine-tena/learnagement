"""Extraction des sections et métadonnées d'une page de détail (formation, UE, module)."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from .program_parser import norm, to_number

HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCKS = {
    "p",
    "div",
    "li",
    "br",
    "tr",
    "section",
    "article",
    "ul",
    "ol",
    "table",
    "dt",
    "dd",
} | HEADINGS

INFO_LABELS = {
    "ects": ["ects"],
    "composante": ["composante"],
    "langues_enseignement": ["langues d enseignement", "langue d enseignement"],
    "ouvert_echange": ["ouvert aux etudiants en echange"],
    "niveau_diplome": ["niveau de diplome"],
    "duree": ["duree"],
    "niveau_entree": ["niveau d entree"],
    "campus": ["campus"],
    "lieux": ["lieux"],
    "regimes_etude": ["regimes d etude"],
    "code_rncp": ["code rncp"],
    "responsables": [
        "responsable",
        "responsables",
        "responsable s",
        "responsable de l enseignement",
    ],
    "enseignants": ["enseignant", "enseignants", "enseignant s", "intervenants"],
    "volume_horaire": ["volume horaire", "volume horaire total", "heures"],
    "semestre": ["semestre", "periode"],
    "coefficient": ["coefficient", "coefficients"],
    "modalites_enseignement": ["modalites d enseignement"],
}
LABEL_LOOKUP = {norm(v): k for k, vs in INFO_LABELS.items() for v in vs}

# Cle canonique <- prefixes de titres de sections (normalises)
CANON = [
    ("presentation", ["presentation", "description", "resume"]),
    ("objectifs", ["objectif"]),
    (
        "prerequis",
        ["prerequis", "pre requis", "connaissances prealables", "pre requis recommandes"],
    ),
    ("plan_du_cours", ["plan du cours", "plan", "contenu", "programme du cours", "syllabus"]),
    ("competences", ["competences", "acquis d apprentissage"]),
    ("bibliographie", ["bibliograph", "ressources", "references"]),
    (
        "modalites_controle",
        [
            "modalites de controle",
            "controle des connaissances",
            "evaluation",
            "modalites d evaluation",
        ],
    ),
]


def canon_key(title: str) -> str | None:
    t = norm(title)
    for key, prefixes in CANON:
        if any(t == p or t.startswith(p) for p in prefixes):
            return key
    return None


def clean_lines(parts: list[str]) -> str:
    text = "".join(parts)
    lines = [re.sub(r"[ \t\u00a0]+", " ", line).strip() for line in text.split("\n")]
    out: list[str] = []
    for line in lines:
        if line or (out and out[-1]):
            out.append(line)
    return "\n".join(out).strip()


def parse_detail(html: str, drop_link_heavy_sections: bool = False) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    meta = {m["name"]: m.get("content") for m in soup.find_all("meta") if m.get("name")}

    for t in soup.find_all(["script", "style", "noscript", "header", "nav", "footer"]):
        t.decompose()
    root = soup.find("main") or soup.find(id="main-content") or soup.body or soup

    h1 = root.find("h1") or soup.find("h1")
    out: dict = {"titre_page": h1.get_text(" ", strip=True) if h1 else None}

    # PDF "Fiche synthetique"
    for a in root.find_all("a", href=True):
        if ".pdf" in a["href"].lower() or "fiche synth" in norm(a.get_text()):
            out["fiche_pdf"] = a["href"]
            break

    # Infos label -> valeur (ligne suivante)
    lines = [line.strip() for line in root.get_text("\n", strip=True).split("\n") if line.strip()]
    infos: dict[str, str] = {}
    for i, line in enumerate(lines[:-1]):
        key = LABEL_LOOKUP.get(norm(line))
        if key and key not in infos:
            infos[key] = lines[i + 1]
    if "ects" in infos:
        out["ects"] = to_number(infos["ects"])
    out["infos"] = infos

    # Sections decoupees par titres (ordre du document)
    sections: dict[str, str] = {}
    for h in root.find_all(sorted(HEADINGS)):
        title = h.get_text(" ", strip=True)
        if not title or h.name == "h1":
            continue
        parts: list[str] = []
        n_links = 0
        inside = {id(x) for x in h.descendants}
        for el in h.next_elements:
            if id(el) in inside:
                continue  # le titre lui-meme
            if isinstance(el, Tag):
                if el.name in HEADINGS:
                    break
                if el.name == "a":
                    n_links += 1
                if el.name in BLOCKS:
                    parts.append("\n")
                if el.name == "li":
                    parts.append("- ")
            elif isinstance(el, NavigableString) and not isinstance(el, Comment):
                parts.append(str(el))
        if drop_link_heavy_sections and n_links > 15:
            continue
        text = clean_lines(parts)
        if not text:
            continue
        key = title
        while key in sections:  # titres dupliques
            key += " (bis)"
        sections[key] = text
    out["sections"] = sections

    for title, text in sections.items():
        c = canon_key(title)
        if c and c not in out:
            out[c] = text

    out["meta"] = {
        k: v for k, v in meta.items() if k in ("DC.identifier", "DC.date", "DC.title", "DC.publisher")
    }
    out["texte_brut"] = "\n".join(lines)
    return out
