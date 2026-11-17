"""Paquet apc20_ens_fiche_module."""

from .callbacks import register_callbacks
from .layout import fiche_module_content

__all__ = [
    "fiche_module_content",
    "register_callbacks",
]
