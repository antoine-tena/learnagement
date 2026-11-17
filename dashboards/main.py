import logging
import os

import dash_bootstrap_components as dbc
from auth import FlaskAuth, decode_token, token_from_cookie
from dash import Input, Output, State, dcc, html
from dotenv import load_dotenv
from flask import jsonify, session
from main_app import (
    LOGO,
    build_menu_items,
    icon_map,
    import_apps,
    render_sidebar as _render_sidebar,
    run_server,
)


class HealthFilter(logging.Filter):
    def filter(self, record):
        return "/health" not in record.getMessage()


logging.getLogger().addFilter(HealthFilter())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
)

load_dotenv()


# Utilisation
app = FlaskAuth(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)

server = app.server
server.secret_key = os.getenv("JWT_SIGNING_KEY")
time_out = int(os.getenv("SESSION_TIMEOUT"))

registered_callbacks = set()

apps = import_apps()

environment = SECRET_KEY = os.getenv("ENV")  # prod or dev
menu_items = build_menu_items(environment)


def render_sidebar(section, status):
    return _render_sidebar(section, status, menu_items)


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="token", storage_type="memory", data="none"),
        dcc.Store(id="user_id", storage_type="memory", data="0"),
        dcc.Store(id="role", storage_type="memory", data="none"),
        dcc.Store(id="status", storage_type="memory", data="not connected"),  # deprecated
        # Stores des dashboards APC — toujours dans le DOM pour que leurs callbacks se déclenchent dès le token disponible
        dcc.Store(id="apc-ens-raw-store"),
        dcc.Location(id="url-redirect", refresh=True),
        html.Div(id="sidebar"),
        html.Div(id="page-content", className="content"),
    ]
)


# Callback pour mettre à jour la sidebar
@app.callback(
    Output("sidebar", "children"),
    Input("url", "href"),
    Input("url", "pathname"),
    Input("status", "data"),
)
def update_sidebar(url, pathname, status):
    logging.info("update_sidebar")
    if pathname and pathname.startswith("/enseignant"):
        return render_sidebar("enseignant", status)
    elif pathname and pathname.startswith("/etudiant"):
        return render_sidebar("etudiant", status)
    elif pathname and pathname.startswith("/administratif"):
        return render_sidebar("administratif", status)
    else:
        # Chemin non reconnu : sidebar vide ou message par défaut
        return html.Div(
            [html.H2("Bienvenue"), html.P("Veuillez sélectionner une section valide dans l'URL.")],
            className="p-3",
        )


# Callback pour rendre le bon contenu
@app.callback(
    Output("page-content", "children"),
    Output("token", "data"),
    Output("user_id", "data"),  # ToDo must be moved to session
    Output("role", "data"),  # ToDo must be moved to session
    Output("status", "data"),  # ToDo must be moved to session
    Input("url", "href"),
    Input("url", "pathname"),
    State("token", "data"),
)
def render_page(url, pathname, token):
    try:
        jwt_token, user_id, main_role, status = check_auth_token(
            url
        )  # if token is none, check_auth_token will get it
        page_content = render_page_content(url, pathname, jwt_token)
        return page_content, jwt_token, user_id, main_role, status
    except Exception as e:
        logging.exception(e)
        instance_protocol = os.getenv("INSTANCE_PROTOCOL")
        instance_url = os.getenv("INSTANCE_URL")
        front_php_port = os.getenv("FRONT_PHP_PORT")
        return (
            html.Div(
                [
                    html.A(
                        href=f"{instance_protocol}://{instance_url}:{front_php_port}/logout",
                        target="_top",
                        children="Session closed, connection required.",
                    )
                ]
            ),
            "-1",
            "none",
            "none",
            "no token",
        )


def check_auth_token(url):
    logging.info("check_auth_token")
    instance_protocol = os.getenv("INSTANCE_PROTOCOL")
    instance_url = os.getenv("INSTANCE_URL")
    front_php_port = os.getenv("FRONT_PHP_PORT")

    jwt_token = token_from_cookie()

    session["token"] = jwt_token

    if not jwt_token:
        logging.info("no token")
        app.layout = html.Div(
            [
                html.A(
                    href=f"{instance_protocol}://{instance_url}:{front_php_port}/logout",
                    target="_top",
                    children="No Token, session closed, connection required.",
                )
            ]
        )
        return "-1", "none", "none", "no token"
    payload = decode_token(jwt_token)
    logging.info("user %s connected", payload["id"])
    if "enseignant" in payload["roles"]:
        return jwt_token, payload["id"], "enseignant", "Connected"
    elif "etudiant" in payload["roles"]:
        return jwt_token, payload["id"], "etudiant", "Connected"
    elif "administratif" in payload["roles"]:
        return jwt_token, payload["id"], "administratif", "Connected"
    else:
        logging.exception("Unknown user class")
        raise Exception("Unknown user class")


def render_page_content(url, pathname, token):
    logging.info("render_page_content")

    parts = pathname.strip("/").split(
        "/"
    )  # ['enseignant', 'app2'] ou ['etudiant','app7'] ou ['enseignant'] etc.
    if len(parts) == 1:
        # page section landing
        return html.Div(
            [
                html.H2(f"Section: {parts[0].capitalize()}"),
                html.P("Sélectionnez une rubrique dans la barre latérale."),
            ],
            className="p-3",
        )
    section, key = parts[0], parts[1]
    if section in menu_items and key in apps:
        layout, register_cb = apps[key]
        if register_cb and key not in registered_callbacks:
            register_cb(app)
            registered_callbacks.add(key)

        return layout
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"La page {pathname} n'existe pas."),
        ],
        className="p-3 bg-light rounded-3",
    )


for key, (_, register_cb) in apps.items():
    if register_cb and key not in registered_callbacks:
        register_cb(app)
        registered_callbacks.add(key)


@server.route("/health")
def health():
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    run_server(app, server)
