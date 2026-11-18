import dash_bootstrap_components as dbc
from dash import dcc, html

# Définition de la mise en page de l'application
app14_administratif_layout = html.Div(
    children=[
        dbc.Button(
            "Séquençage VS Maquette",
            id="collapse-button1",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="table_sequencage_vs_maquette"),
                ],
            ),
            id="collapse1",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "Modules sans UE",
            id="collapse-button2",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="table_modules_sans_ue"),
                ],
            ),
            id="collapse2",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "Modules sans AC",
            id="collapse-button3",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="table_modules_sans_ac"),
                ],
            ),
            id="collapse3",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "Enseignant sans cours",
            id="collapse-button4",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="div_enseignant_sans_cours"),
                ],
            ),
            id="collapse4",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "Session sans enseignant",
            id="collapse-button5",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="div_session_sans_enseignant"),
                ],
            ),
            id="collapse5",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "Poids ECTS",
            id="collapse-button6",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="div_modules_ects"),
                ],
            ),
            id="collapse6",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "Corruption d'intégrité référentielle dans la table session",
            id="collapse-button7",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="div_session_corruption"),
                ],
            ),
            id="collapse7",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "Graph des permissions",
            id="collapse-button8",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[dcc.Input(id="fake", value="0", type="hidden"), html.Div(id="div_auth")],
            ),
            id="collapse8",
            is_open=False,
        ),
        html.Br(),
        dbc.Button(
            "DAG des permissions",
            id="collapse-button9",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            html.Div(
                style={
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
                children=[
                    dcc.Input(id="fake", value="0", type="hidden"),
                    html.Div(id="div_auth_tree_sqlglot"),
                ],
            ),
            id="collapse9",
            is_open=False,
        ),
    ]
)
