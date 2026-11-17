"""Commandes CLI fetch et reparse pour ical2json."""

import sys
from pathlib import Path

from .ical_reader import ErreurImport, decoder, horodatage, lire_source
from .parser import PARSER_VERSION
from .snapshots import (
    analyser,
    archiver_rejet,
    construire_json,
    ecrire_json_fichier,
    ecrire_snapshot_json,
    lire_json,
    nettoyer,
    now_iso,
    refs_hash,
    sha256,
)


def cmd_fetch(args, refs) -> int:
    racine = Path(args.racine)
    data = None
    try:
        data = lire_source(args.source)
        raw, events, filiere, hors = analyser(decoder(data), refs, args.filiere, args.tolerance)
        horo = horodatage(raw)
    except ErreurImport as e:
        d = archiver_rejet(racine, args.source, data, e)
        print(f"Import refusé, détails conservés dans {d}", file=sys.stderr)
        raise

    dest = racine / nettoyer(filiere) / horo
    if dest.exists():
        existant = dest / "edt.ics"
        if existant.exists() and sha256(existant.read_bytes()) == sha256(data):
            print(f"Déjà importé : {dest} (rien à faire)")
            return 0
        raise ErreurImport(
            f"Le dossier {dest} existe déjà avec un contenu différent.",
            {"astuce": "Deux exports différents à la même minute : vérifier à la main."},
        )

    dest.mkdir(parents=True)
    (dest / "edt.ics").write_bytes(data)
    manifest = {
        "filiere": filiere,
        "source": args.source,
        "source_sha256": sha256(data),
        "tolerance": args.tolerance,
        "importe_le": now_iso(),
        "parsings": [],
    }
    ecrire_snapshot_json(
        dest, construire_json(events, filiere, hors, data, args.source, horo, refs), manifest
    )
    msg = f"OK : {len(events)} événements, filière {filiere} -> {dest}"
    if hors:
        msg += f" ({len(hors)} événement(s) hors filière tolérés, voir meta.uid_hors_filiere)"
    print(msg)
    return 0


def cmd_reparse(args, refs) -> int:
    racine = Path(args.racine)
    rh = refs_hash(refs)
    refaits, ignores, erreurs = 0, 0, []

    for ics in sorted(racine.glob("*/*/edt.ics")):
        dest = ics.parent
        fil_dir = dest.parent.name
        if fil_dir.startswith("_") or (args.filiere and fil_dir != args.filiere):
            continue
        manifest = lire_json(dest / "manifest.json") or {}
        dernier = (manifest.get("parsings") or [{}])[-1]
        a_jour = (
            dernier.get("parser_version") == PARSER_VERSION
            and dernier.get("refs_sha256") == rh
            and (dest / "edt.json").exists()
        )
        if a_jour and not args.force:
            ignores += 1
            continue
        try:
            data = ics.read_bytes()
            raw, events, filiere, hors = analyser(
                decoder(data), refs, fil_dir, manifest.get("tolerance", 0)
            )
            horo = dest.name
            manifest.setdefault("filiere", filiere)
            manifest.setdefault("source", "inconnue")
            manifest.setdefault("source_sha256", sha256(data))
            manifest.setdefault("tolerance", 0)
            # Le nouveau JSON est construit AVANT d'archiver l'ancien : en cas d'erreur, rien n'est modifié.
            ecrire_snapshot_json(
                dest,
                construire_json(events, filiere, hors, data, manifest["source"], horo, refs),
                manifest,
            )
            refaits += 1
            print(f"reparsé : {dest} (v{PARSER_VERSION})")
        except ErreurImport as e:
            erreurs.append((str(dest), str(e), e.details))
            print(f"ERREUR sur {dest} : {e}", file=sys.stderr)

    print(f"\n{refaits} reparsé(s), {ignores} déjà à jour, {len(erreurs)} en erreur.")
    if erreurs:
        ecrire_json_fichier(
            racine / "_reparse_erreurs.json",
            [{"snapshot": s, "message": m, "details": d} for s, m, d in erreurs],
        )
        print(f"Détails des erreurs : {racine / '_reparse_erreurs.json'}", file=sys.stderr)
        return 1
    return 0
