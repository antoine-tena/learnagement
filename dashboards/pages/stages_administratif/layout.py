from datetime import date, datetime

from clock import today_in_paris

import dash_bootstrap_components as dbc
from dash import dcc, html

from .queries import update_pie_chart


def app10_administratif_layout() -> html.Div:
    """La page des stages, ses dates par défaut calculées à chaque affichage."""
    return html.Div(
        children=[
            html.H1(children="Gestion des Stages"),
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    html.H2(children="Sélection de promo"),
                    dcc.Dropdown(
                        id="app10_filtre_promo",
                        options=[],
                        placeholder="Sélectionnez une promotion",
                    ),
                ],
            ),
            html.Div(
                id="div_pie_chart",
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[update_pie_chart(token=None)],
            ),
            html.Br(),
            html.Div(
                [
                    html.H2(children="Nouveau stage"),
                    dcc.Input(id="stage_id", value="0", type="hidden"),
                    dbc.Row(
                        [
                            dbc.Label("Etudiant", html_for="etudiant_input", width=2),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="etudiant_input",
                                    options=[],
                                    placeholder="Please select student",
                                ),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Label("Entreprise", html_for="entreprise_input", width=2),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="entreprise_input",
                                    options=[],
                                    placeholder="Please enter the entreprise name",
                                    search_value="",
                                    clearable=True,
                                ),
                                width=8,
                            ),
                            dbc.Input(id="new_entreprise_input", type="hidden", value=""),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Label("Sujet", html_for="sujet_input", width=2),
                            dbc.Col(
                                dbc.Input(id="sujet_input", placeholder="Please enter the subject"),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Label("Mission", html_for="mission_input", width=2),
                            dbc.Col(
                                dbc.Textarea(
                                    id="mission_input", placeholder="Please enter the mission"
                                ),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Label("Ville", html_for="ville_input", width=2),
                            dbc.Col(
                                dbc.Input(
                                    id="ville_input", placeholder="Please enter the location"
                                ),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Label("Dates", html_for="dates_input", width=2),
                            dbc.Col(
                                dcc.DatePickerRange(
                                    id="dates_input",
                                    min_date_allowed=date(2025, 1, 1),
                                    max_date_allowed=date(2026, 12, 31),
                                    initial_visible_month=today_in_paris(),
                                    start_date=today_in_paris(),
                                    end_date=today_in_paris(),
                                ),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Label("Tuteur", html_for="tuteur_input", width=2),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="tuteur_input",
                                    options=[],
                                    placeholder="Please select tuteur",
                                    value="",
                                ),
                                width=8,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Button(
                                "Save the data",
                                id="submit-button",
                                color="primary",
                                outline=True,
                                disabled=False,
                            )
                        ],
                        className="mb-3",
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    html.H2(children="Stage avec tuteur"),
                    html.Div(id="div_stages_with_supervisor"),
                ],
            ),
            html.Br(),
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    html.H2(children="Stage sans tuteur"),
                    html.Div(id="div_stages_without_supervisor"),
                ],
            ),
            html.Br(),
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    html.H2(children="Etudiants sans stage"),
                    html.Div(id="div_students_without_stage"),
                ],
            ),
        ]
    )
