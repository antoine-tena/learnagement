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


def render(main_module: ModuleType, pathname: str, role: str) -> str:
    return str(main_module.render_page_content("", pathname, "jeton", role))


@pytest.mark.parametrize("role", ROLES)
def test_own_pages_render(main_module: ModuleType, role: str) -> None:
    for _label, key in build_menu_items("dev")[role]:
        layout, _register = main_module.apps[key]
        expected = str(layout() if callable(layout) else layout)
        assert render(main_module, f"/{role}/{key}", role) == expected


@pytest.mark.parametrize("role", ROLES)
def test_own_section_renders_its_landing(main_module: ModuleType, role: str) -> None:
    assert f"Section: {role.capitalize()}" in render(main_module, f"/{role}", role)


@pytest.mark.parametrize(("role", "other"), [(r, o) for r in ROLES for o in ROLES if r != o])
def test_pages_of_another_role_are_forbidden(
    main_module: ModuleType, role: str, other: str
) -> None:
    for _label, key in build_menu_items("dev")[other]:
        assert "403" in render(main_module, f"/{other}/{key}", role), (role, other, key)
    assert "403" in render(main_module, f"/{other}", role)


@pytest.mark.parametrize("role", ROLES)
def test_page_out_of_the_role_menu_is_forbidden(main_module: ModuleType, role: str) -> None:
    own = {key for _label, key in build_menu_items("dev")[role]}
    for key in sorted(set(main_module.apps) - own):
        assert "403" in render(main_module, f"/{role}/{key}", role), (role, key)


@pytest.mark.parametrize("pathname", ["/etudiant/page_inconnue", "/inconnu/app10_etudiant"])
def test_unknown_url_renders_a_404(main_module: ModuleType, pathname: str) -> None:
    assert "404" in render(main_module, pathname, "etudiant")
