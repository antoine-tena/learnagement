"""Paquet de scraping du catalogue des formations USMB (Ametys / ODF)."""

from .assembly import enrich, finalize, walk
from .detail_parser import (
    BLOCKS,
    CANON,
    HEADINGS,
    INFO_LABELS,
    LABEL_LOOKUP,
    canon_key,
    clean_lines,
    parse_detail,
)
from .fetcher import Fetcher
from .program_parser import (
    contact_hours,
    group_constraints,
    norm,
    own_text,
    parse_constraint,
    parse_program,
    parse_row,
    semester_of,
    split_code,
    to_number,
)

__all__ = [
    "BLOCKS",
    "CANON",
    "Fetcher",
    "HEADINGS",
    "INFO_LABELS",
    "LABEL_LOOKUP",
    "canon_key",
    "clean_lines",
    "contact_hours",
    "enrich",
    "finalize",
    "group_constraints",
    "norm",
    "own_text",
    "parse_constraint",
    "parse_detail",
    "parse_program",
    "parse_row",
    "semester_of",
    "split_code",
    "to_number",
    "walk",
]
