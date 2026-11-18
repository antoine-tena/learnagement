"""Décomposition des champs d'événements ADE et construction des référentiels."""

import re
from zoneinfo import ZoneInfo

from .ical_reader import norm, parse_dt, unescape

# À INCRÉMENTER à chaque modification de la logique d'analyse :
# c'est ce qui déclenche le reparsing des anciens snapshots.
PARSER_VERSION = "1.1.0"

TZ = ZoneInfo("Europe/Paris")

DEFAULT_REFS = {
    "enseignants": [
        "VIGNAND SYLVIE",
        "SALAMATIAN MOHAMMAD-REZA",
        "CLARK JULIE",
        "ENRIQUEZ CISNEROS DIANA-IRAIS",
        "GRAY ALICE",
        "BASCOP ALEXANDRE",
        "CIMPAN SORANA",
        "PETIT WILFRIED",
        "FERRER ROMAIN",
        "ATTO ABDOURRAHMANE",
        "CHOAIB MOHAMMAD",
        "PELINKU Sara",
    ],
    "salles": ["A-C215 (52pl.)", "A-C214 (32pl.)", "A-B120 (150pl.)"],
    "groupes": [
        "IDU-4-Promo",
        "IDU-4-A",
        "IDU-4-A1",
        "IDU-4-A2",
        "IDU-4",
        "IDU-5",
        "MECA-FISE-4",
        "MECA-FISE-3",
        "SNI-4",
        "SNI-5",
    ],
    "filieres": [
        "IDU",
        "SEA",
        "MECA",
        "SNI",
        "EPU",
        "BAT",
        "EN",
        "IB",
        "EIT",
        "MC",
        "ITII",
        "Master",
    ],
    "statuts": ["FISE", "FISA"],
    "types_cours": [
        "CM",
        "TD",
        "TP",
        "EXAMEN",
        "EXAMEN SESSION 2",
        "PROJET",
        "REUNION",
        "TUTORAT",
        "ACTIVITE ASSOCIATIVE",
        "ACCUEIL-RENTREE",
    ],
}

ROOM_RE = re.compile(r"^(?P<nom>.*?)\s*\((?P<cap>\d+)\s*pl\.\)\s*$")
ROOM_ID_RE = re.compile(r"^(?P<bat>[A-Z])-(?P<salle>\S+)")
CODE_RE = re.compile(r"(?<![A-Za-z])([A-Z]{2,5})\s?(\d{3})(?!\d)")
TITLE_TYPE_RE = re.compile(r"^(?P<titre>.*?)\s*\((?P<type>[^()]*)\)\s*$")


def parse_rooms(raw_location: str, known_rooms: set[str]) -> list[dict]:
    rooms = []
    for part in re.split(r"(?<!\\),", raw_location or ""):
        part = unescape(part).strip()
        if not part:
            continue
        m = ROOM_RE.match(part)
        nom = m["nom"] if m else part
        mid = ROOM_ID_RE.match(nom)
        rooms.append(
            {
                "nom": nom,
                "capacite": int(m["cap"]) if m else None,
                "batiment": mid["bat"] if mid else None,
                "salle": mid["salle"] if mid else None,
                "distanciel": nom.lower().startswith("distanciel"),
                "connue": norm(nom) in known_rooms,
            }
        )
    return rooms


def parse_group(name: str, filieres: set, statuts: set, connu: bool = True) -> dict:
    tokens = [t for t in re.split(r"[-_]", name) if t]
    statut, annee, reste = None, None, []
    for t in tokens[1:]:
        if t.upper() in statuts:
            statut = t.upper()
        elif t.isdigit() and annee is None:
            annee = int(t)
        else:
            reste.append(t)
    return {
        "nom": name,
        "connu": connu,
        "filiere": tokens[0] if tokens else None,
        "filiere_connue": bool(tokens) and tokens[0] in filieres,
        "statut": statut,
        "annee": annee,
        "sous_groupe": "-".join(reste) or None,
    }


def looks_like_group(item: str, filieres: set) -> bool:
    """Groupe absent de la liste, mais dont le préfixe est une filière connue."""
    return bool(
        re.fullmatch(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", item)
        and re.split(r"[-_]", item)[0] in filieres
    )


def decode_uid(uid: str):
    """ADE60<hex> -> 'Savoie2026-2027-12759-0-5' -> (12759, [0, 5])"""
    m = re.fullmatch(r"ADE60([0-9a-fA-F]+)", uid or "")
    if not m or len(m[1]) % 2:
        return None, None
    try:
        s = bytes.fromhex(m[1]).decode("ascii")
    except (ValueError, UnicodeDecodeError):
        return None, None
    m = re.search(r"-(\d+)-(\d+)-(\d+)$", s)
    return (int(m[1]), [int(m[2]), int(m[3])]) if m else (None, None)


def parse_description(raw: str, refs: dict) -> dict:
    groups_idx = {g.casefold(): g for g in refs["groupes"]}
    teachers_idx = {norm(t): t for t in refs["enseignants"]}
    filieres = set(refs["filieres"])
    statuts = {s.upper() for s in refs["statuts"]}

    head_raw, _, tail_raw = raw.partition("(Exporté le:")

    lines = [unescape(line).strip() for line in re.split(r"\\[nN]", head_raw)]
    first = lines[0] if lines else ""
    m = TITLE_TYPE_RE.match(first)
    titre = m["titre"].strip() if m else first
    type_raw = (m["type"].strip() if m else "") or None

    groupes, enseignants, ressources, autres = [], [], [], []
    for it in (line for line in lines[1:] if line):
        if it.casefold() in groups_idx:
            groupes.append(parse_group(groups_idx[it.casefold()], filieres, statuts))
        elif norm(it) in teachers_idx:
            enseignants.append(
                {
                    "nom": teachers_idx[norm(it)],
                    "provisoire": bool(re.search(r"\(provisoire\)", it, re.I)),
                }
            )
        elif looks_like_group(it, filieres):
            groupes.append(parse_group(it, filieres, statuts, connu=False))
        elif it.isdigit():
            ressources.append(it)
        else:
            autres.append(it)

    export_le = None
    m = re.match(r"^([^)]*)\)", tail_raw)
    if m:
        export_le = m.group(1).strip()
        tail_raw = tail_raw[m.end() :]
    parts = [re.sub(r"(\\[nN])+", " ", p).strip() for p in re.split(r"\\,", tail_raw)]
    parts += [""] * (3 - len(parts))

    return {
        "titre": titre or None,
        "type_cours": type_raw,
        "type_connu": (type_raw in refs["types_cours"]) if type_raw else None,
        "groupes": groupes,
        "enseignants": enseignants,
        "ressources": ressources,
        "non_classes": autres,
        "export_le": export_le,
        "nom_module": parts[0] or None,
        "code_ue": parts[1] or None,
        "extra": parts[2] or None,
    }


def convert_event(ev: dict, refs: dict, known_rooms: set[str]) -> dict:
    start, end = parse_dt(ev["DTSTART"]), parse_dt(ev["DTEND"])
    desc = parse_description(ev.get("DESCRIPTION", ""), refs)
    summary = unescape(ev.get("SUMMARY", "")).strip()
    m = CODE_RE.search(desc["titre"] or "") or CODE_RE.search(summary)
    start_l, end_l = start.astimezone(TZ), end.astimezone(TZ)
    groupes = desc["groupes"]
    id_activite, uid_indices = decode_uid(ev.get("UID"))

    return {
        "uid": ev.get("UID"),
        "id_activite": id_activite,
        "uid_indices": uid_indices,
        "resume": summary,
        "code_matiere": f"{m.group(1)}{m.group(2)}" if m else None,
        "titre": desc["titre"],
        "nom_module": desc["nom_module"],
        "code_ue": desc["code_ue"],
        "type_cours": desc["type_cours"],
        "type_connu": desc["type_connu"],
        "debut": start_l.isoformat(),
        "fin": end_l.isoformat(),
        "debut_utc": start.isoformat(),
        "fin_utc": end.isoformat(),
        "date": start_l.date().isoformat(),
        "jour_semaine": start_l.strftime("%A"),
        "duree_minutes": int((end - start).total_seconds() // 60),
        "salles": parse_rooms(ev.get("LOCATION", ""), known_rooms),
        "enseignants": desc["enseignants"],
        "groupes": groupes,
        "filieres": sorted({g["filiere"] for g in groupes if g["filiere"]}),
        "statuts": sorted({g["statut"] for g in groupes if g["statut"]}),
        "ressources": desc["ressources"],
        "non_classes": desc["non_classes"],
        "extra": desc["extra"],
        "export_le": desc["export_le"],
        "cree_le": ev.get("CREATED"),
        "modifie_le": ev.get("LAST-MODIFIED"),
        "dtstamp": ev.get("DTSTAMP"),
        "sequence": int(ev["SEQUENCE"]) if ev.get("SEQUENCE", "").isdigit() else None,
    }


def build_referentiels(events: list[dict]) -> dict:
    return {
        "enseignants": sorted({e["nom"] for ev in events for e in ev["enseignants"]}),
        "salles": sorted({(s["nom"], s["capacite"]) for ev in events for s in ev["salles"]}),
        "groupes": sorted({g["nom"] for ev in events for g in ev["groupes"]}),
        "filieres": sorted({f for ev in events for f in ev["filieres"]}),
        "statuts": sorted({s for ev in events for s in ev["statuts"]}),
        "types_cours": sorted({ev["type_cours"] for ev in events if ev["type_cours"]}),
        "modules": sorted(
            {(ev["code_matiere"], ev["nom_module"]) for ev in events if ev["code_matiere"]}
        ),
    }
