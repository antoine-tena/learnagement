"""Rendu de la barre latérale de navigation Dash."""

import os

import dash_bootstrap_components as dbc
from dash import html

from .registry import icon_map

LOGO = "https://placehold.co/100x100"


def render_sidebar(section, status, menu_items):
    # AJOUTE CES DEUX LIGNES POUR LE DÉBOGAGE :
    print(f"====== CRÉATION DU MENU POUR : {section} ======", flush=True)
    print(f"====== CONTENU DU MENU : {menu_items[section]} ======", flush=True)
    links = []
    # Logo + titre
    links.append(
        html.Div(
            [html.Img(src=LOGO, style={"width": "3rem"}), html.H2(section.capitalize())],
            className="sidebar-header",
        )
    )
    links.append(html.Hr())
    # Navigation
    navs = []
    for label, key in menu_items[section]:
        href = f"/{section}/{key}"
        icon_class = icon_map.get(key, "fa-solid fa-circle")  # icône par défaut si manquante
        navs.append(
            dbc.NavLink(
                [html.I(className=icon_class, style={"marginRight": "2rem"}), label],
                href=href,
                id=f"link-{key}",
                className="menu-item",
            )
        )
    navs.append(html.Hr())
    instance_protocol = os.getenv("INSTANCE_PROTOCOL")
    instance_url = os.getenv("INSTANCE_URL")
    php_port = os.getenv("FRONT_PHP_PORT")
    icon_class = icon_map.get("dashboard", "fa-solid fa-circle")
    navs.append(
        dbc.NavLink(
            [html.I(className=icon_class, style={"marginRight": "2rem"}), "PHP Dashboard"],
            href=f"{instance_protocol}://{instance_url}:{php_port}",
            id="link-php-dashboard",
            className="menu-item",
        )
    )
    env = os.getenv("ENV")
    if env == "dev":
        next_auth_port = os.getenv("FRONT_NEXTAUTH_PORT")
        navs.append(
            dbc.NavLink(
                [html.I(className=icon_class, style={"marginRight": "2rem"}), "NextJS Dashboard"],
                href=f"{instance_protocol}://{instance_url}:{next_auth_port}",
                id="link-php-dashboard",
                className="menu-item",
            )
        )
    icon_class = icon_map.get("exit", "fa-solid fa-circle")
    navs.append(
        dbc.NavLink(
            [html.I(className=icon_class, style={"marginRight": "2rem"}), "Déconnexion"],
            href=f"{instance_protocol}://{instance_url}:{php_port}/logout",
            id="link-php-dashboard",
            className="menu-item",
        )
    )

    links.append(dbc.Nav(navs, vertical=True, pills=True))

    return html.Div(
        links,
        className="sidebar",
        style={"overflowY": "auto", "maxHeight": "100vh", "paddingBottom": "50px"},
    )
