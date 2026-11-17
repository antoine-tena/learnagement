#!/usr/bin/env python3
"""
Import d'emplois du temps ADE (iCal) -> snapshots JSON versionnés.

  python edt_snapshots.py [--racine snapshots] [--config refs.json] fetch <URL|fichier.ics> [--filiere IDU] [--tolerance 0]
  python edt_snapshots.py [--racine snapshots] [--config refs.json] reparse [--filiere IDU] [--force]

Arborescence produite :
  snapshots/<FILIERE>/<AAAA-MM-JJTHHMMZ>/edt.ics        (source brute)
                                         edt.json        (dernier parsing)
                                         edt.v<version>.json  (anciens parsings)
                                         manifest.json   (historique des parsings)
  snapshots/_rejets/<horodatage>/                         (imports refusés, pour intervention humaine)
"""
import argparse
import json
import sys

from ical2json_lib import DEFAULT_REFS, ErreurImport, cmd_fetch, cmd_reparse


def main():
    ap = argparse.ArgumentParser(description="Snapshots JSON d'emplois du temps ADE")
    ap.add_argument("--racine", default="snapshots")
    ap.add_argument("--config", help="JSON des listes de référence")
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="télécharger, valider et stocker un iCal")
    f.add_argument("source", help="URL de l'iCal (ou chemin d'un .ics local)")
    f.add_argument("--filiere", help="filière attendue (sinon déduite du contenu)")
    f.add_argument(
        "--tolerance",
        type=int,
        default=0,
        help="nb d'événements transversaux autorisés hors filière (défaut 0)",
    )

    r = sub.add_parser("reparse", help="reparser les .ics existants")
    r.add_argument("--filiere", help="limiter à une filière")
    r.add_argument(
        "--force",
        action="store_true",
        help="reparser même si version et référentiels sont à jour",
    )

    args = ap.parse_args()
    refs = dict(DEFAULT_REFS)
    if args.config:
        with open(args.config, encoding="utf-8") as fh:
            refs.update(json.load(fh))

    try:
        code = cmd_fetch(args, refs) if args.cmd == "fetch" else cmd_reparse(args, refs)
    except ErreurImport as e:
        print(f"ERREUR : {e}", file=sys.stderr)
        if e.details:
            print(json.dumps(e.details, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(2)
    sys.exit(code)


if __name__ == "__main__":
    main()
