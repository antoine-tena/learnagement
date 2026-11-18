"""Chaque page du menu existe, se construit, et l'URL mène à la bonne page ou à une page 404."""

import importlib
from types import ModuleType

import pytest
from dash.development.base_component import Component

from main_app.registry import build_menu_items

ENVIRONMENTS = ("dev", "prod")
ROLES = ("administratif", "enseignant", "etudiant")


@pytest.fixture(scope="module")
def main_module() -> ModuleType:
    """`main.py` importé comme au démarrage du conteneur : toutes les pages enregistrées."""
    with pytest.MonkeyPatch.context() as env:
        env.setenv("ENV", "dev")
        env.setenv("SESSION_TIMEOUT", "3600")
        env.setenv("JWT_SIGNING_KEY", "cle-de-test-uniquement-pour-les-tableaux-de-bord")
        return importlib.import_module("main")


def menu_keys(environment: str) -> set[str]:
    menu = build_menu_items(environment)
    return {key for entries in menu.values() for _, key in entries}


def test_every_role_has_a_menu() -> None:
    for environment in ENVIRONMENTS:
        assert set(build_menu_items(environment)) == set(ROLES)


def test_production_menu_is_part_of_the_dev_menu() -> None:
    assert menu_keys("prod") <= menu_keys("dev")


@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_every_menu_entry_is_a_registered_page(main_module: ModuleType, environment: str) -> None:
    assert menu_keys(environment) <= set(main_module.apps)


@pytest.mark.parametrize("key", sorted(menu_keys("dev")))
def test_every_menu_page_builds(main_module: ModuleType, key: str) -> None:
    layout, _register = main_module.apps[key]
    page = layout() if callable(layout) else layout
    assert isinstance(page, Component)


def test_url_of_a_page_renders_that_page(main_module: ModuleType) -> None:
    layout, _register = main_module.apps["app10_etudiant"]
    page = main_module.render_page_content("", "/etudiant/app10_etudiant", "jeton")
    assert str(page) == str(layout() if callable(layout) else layout)


def test_url_of_a_section_renders_its_landing(main_module: ModuleType) -> None:
    page = main_module.render_page_content("", "/enseignant", "jeton")
    assert "Section: Enseignant" in str(page)


@pytest.mark.parametrize(
    "pathname",
    ["/etudiant/page_inconnue", "/inconnu/app10_etudiant"],
)
def test_unknown_url_renders_a_404(main_module: ModuleType, pathname: str) -> None:
    page = main_module.render_page_content("", pathname, "jeton")
    assert "404" in str(page)
