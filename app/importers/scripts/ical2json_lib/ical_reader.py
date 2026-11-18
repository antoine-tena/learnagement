"""Lecture, décodage et validation structurelle des fichiers iCal ADE."""

import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


class ErreurImport(Exception):
    """Erreur nécessitant une intervention humaine."""

    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details


def lire_source(src: str) -> bytes:
    if re.match(r"^https?://", src, re.I):
        req = urllib.request.Request(src, headers={"User-Agent": "learnagement-scraper/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            raise ErreurImport(f"Téléchargement refusé : HTTP {e.code} {e.reason}", {"url": src})
        except urllib.error.URLError as e:
            raise ErreurImport(f"URL inaccessible : {e.reason}", {"url": src})
        except OSError as e:  # timeout, connexion coupée...
            raise ErreurImport(f"Erreur réseau : {e}", {"url": src})
    try:
        return Path(src).read_bytes()
    except OSError as e:
        raise ErreurImport(f"Fichier illisible : {e}", {"fichier": src})


def decoder(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise ErreurImport(f"Le contenu n'est pas de l'UTF-8 valide : {e}")


def unfold(text: str) -> str:
    return re.sub(r"\r?\n[ \t]", "", text)


def unescape(s: str) -> str:
    return re.sub(r"\\(.)", lambda m: "\n" if m.group(1) in "nN" else m.group(1), s)


def parse_vevents(text: str) -> list[dict]:
    events, cur = [], None
    for line in unfold(text).splitlines():
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            name, value = line.split(":", 1)
            cur[name.split(";")[0].upper()] = value
    return events


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)


def valider_ics(text: str) -> list[dict]:
    t = text.strip()
    if not t.startswith("BEGIN:VCALENDAR") or not t.endswith("END:VCALENDAR"):
        raise ErreurImport(
            "Le contenu reçu n'est pas un calendrier iCal (BEGIN/END:VCALENDAR absent). "
            "Page de connexion ou d'erreur ?",
            {"debut_du_contenu": t[:300]},
        )
    raw = parse_vevents(text)
    if not raw:
        raise ErreurImport("Le calendrier ne contient aucun événement (VEVENT).")
    problemes = []
    for i, e in enumerate(raw):
        for champ in ("UID", "SUMMARY", "DTSTART", "DTEND"):
            if not e.get(champ):
                problemes.append(f"événement #{i} ({e.get('UID', '?')}) : champ {champ} manquant")
        try:
            if parse_dt(e["DTEND"]) <= parse_dt(e["DTSTART"]):
                problemes.append(f"événement #{i} ({e.get('UID', '?')}) : fin <= début")
        except (KeyError, ValueError) as ex:
            problemes.append(f"événement #{i} ({e.get('UID', '?')}) : date invalide ({ex})")
    if problemes:
        raise ErreurImport(
            f"{len(problemes)} problème(s) de structure iCal", {"problemes": problemes[:50]}
        )
    return raw


def horodatage(raw_events: list[dict]) -> str:
    """Date de l'export = plus grand DTSTAMP (ex. 20261103T201415Z -> 2026-11-03T2014Z)."""
    stamps = [e["DTSTAMP"] for e in raw_events if e.get("DTSTAMP")]
    if not stamps:
        raise ErreurImport("Aucun DTSTAMP : impossible de dater l'export.")
    return parse_dt(max(stamps)).strftime("%Y-%m-%dT%H%MZ")


def norm(s: str) -> str:
    s = re.sub(r"\(provisoire\)", "", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip().casefold()
