"""Validation de la filière et écriture des snapshots JSON versionnés."""

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .ical_reader import ErreurImport, norm, valider_ics
from .parser import PARSER_VERSION, ROOM_RE, build_referentiels, convert_event


def detecter_filiere(events: list[dict], attendue: str | None, tolerance: int):
    compteur = Counter(f for ev in events for f in set(ev["filieres"]))
    if not compteur:
        raise ErreurImport(
            "Aucune filière détectable dans les groupes des événements.",
            {"astuce": "Compléter la liste 'groupes' / 'filieres' de la configuration."},
        )
    if attendue:
        filiere = attendue
    else:
        top = compteur.most_common(2)
        if len(top) == 2 and top[0][1] == top[1][1]:
            raise ErreurImport(
                "Filière ambiguë : plusieurs filières à égalité.",
                {"repartition": dict(compteur)},
            )
        filiere = top[0][0]

    hors = [ev for ev in events if filiere not in ev["filieres"]]
    if len(hors) > tolerance:
        raise ErreurImport(
            f"{len(hors)} événement(s) sur {len(events)} ne concernent pas la filière « {filiere} » "
            f"(tolérance : {tolerance}).",
            {
                "repartition_filieres": dict(compteur),
                "evenements_hors_filiere": [
                    {
                        "uid": e["uid"],
                        "resume": e["resume"],
                        "debut": e["debut"],
                        "groupes": [g["nom"] for g in e["groupes"]],
                    }
                    for e in hors[:50]
                ],
            },
        )
    return filiere, hors


def analyser(text: str, refs: dict, filiere_attendue: str | None, tolerance: int):
    raw = valider_ics(text)
    known_rooms = {
        norm(ROOM_RE.match(r)["nom"] if ROOM_RE.match(r) else r) for r in refs["salles"]
    }
    events = sorted(
        (convert_event(e, refs, known_rooms) for e in raw), key=lambda e: e["debut_utc"]
    )
    filiere, hors = detecter_filiere(events, filiere_attendue, tolerance)
    return raw, events, filiere, hors


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def refs_hash(refs: dict) -> str:
    return sha256(json.dumps(refs, sort_keys=True, ensure_ascii=False).encode())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def nettoyer(nom: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", nom)


def lire_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def ecrire_json_fichier(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def construire_json(events, filiere, hors, data, source, horo, refs) -> dict:
    return {
        "meta": {
            "filiere": filiere,
            "source": source,
            "source_sha256": sha256(data),
            "horodatage_export": horo,
            "parser_version": PARSER_VERSION,
            "refs_sha256": refs_hash(refs),
            "genere_le": now_iso(),
            "fuseau": "Europe/Paris",
            "nb_evenements": len(events),
            "uid_hors_filiere": [e["uid"] for e in hors],
        },
        "evenements": events,
        "referentiels": build_referentiels(events),
    }


def ecrire_snapshot_json(dest: Path, data_json: dict, manifest: dict):
    """Écrit edt.json ; l'ancien edt.json est conservé sous edt.v<version>.json."""
    cible = dest / "edt.json"
    if cible.exists():
        ancien = lire_json(cible) or {}
        v = ancien.get("meta", {}).get("parser_version", "inconnue")
        archive = dest / f"edt.v{v}.json"
        n = 1
        while archive.exists():
            archive = dest / f"edt.v{v}.{n}.json"
            n += 1
        cible.rename(archive)
        for p in manifest.get("parsings", []):
            if p.get("fichier") == "edt.json":
                p["fichier"] = archive.name
    ecrire_json_fichier(cible, data_json)
    manifest.setdefault("parsings", []).append(
        {
            "fichier": "edt.json",
            "parser_version": data_json["meta"]["parser_version"],
            "refs_sha256": data_json["meta"]["refs_sha256"],
            "genere_le": data_json["meta"]["genere_le"],
        }
    )
    ecrire_json_fichier(dest / "manifest.json", manifest)


def archiver_rejet(racine: Path, source: str, data, err: ErreurImport) -> Path:
    d = racine / "_rejets" / datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    d.mkdir(parents=True, exist_ok=True)
    if data:
        (d / "recu.ics").write_bytes(data)
    ecrire_json_fichier(
        d / "erreur.json",
        {"source": source, "message": str(err), "details": err.details, "date": now_iso()},
    )
    return d
