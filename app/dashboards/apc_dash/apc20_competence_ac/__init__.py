"""Paquet apc20_competence_ac."""

from .callbacks import register_callbacks
from .layout import COLOR_MAP, apc20_competence_ac_layout

__all__ = [
    "COLOR_MAP",
    "apc20_competence_ac_layout",
    "register_callbacks",
]
