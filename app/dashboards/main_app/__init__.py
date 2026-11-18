"""Paquet support du point d'entrée Dash (main.py)."""

from .registry import build_menu_items, icon_map, import_apps
from .server_runner import run_server
from .sidebar import LOGO, render_sidebar

__all__ = [
    "LOGO",
    "build_menu_items",
    "icon_map",
    "import_apps",
    "render_sidebar",
    "run_server",
]
