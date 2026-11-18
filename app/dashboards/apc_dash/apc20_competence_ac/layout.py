"""Layout du tableau de bord Compétences / AC et CE."""

from dash import dcc, html

COLOR_MAP = {
    "COMP_IDU1": "#FF4E3A",
    "COMP_IDU2": "#F39C3D",
    "COMP_IDU3": "#3F7EE8",
    "COMP_IDU4": "#1FB985",
}

apc20_competence_ac_layout = html.Div(
    [
        # STORE AC
        dcc.Store(id="competence-data-store"),
        # STORE CE
        dcc.Store(id="competence-ce-data-store"),
        # PARTIE 1 : COMPETENCE / APPRENTISSAGES CRITIQUES
        html.H3("Compétences et Apprentissages critiques", style={"marginBottom": "20px"}),
        html.Div(
            [
                html.Label("Choisir une compétence :"),
                dcc.Dropdown(
                    id="competence-dropdown", placeholder="Choisir une compétence", clearable=False
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="competence-graph")],
                    style={"width": "60%", "display": "inline-block", "verticalAlign": "top"},
                ),
                html.Div(
                    [html.Div(id="competence_ac")],
                    style={
                        "width": "38%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "paddingLeft": "20px",
                        "maxHeight": "520px",
                        "overflowY": "auto",
                    },
                ),
            ],
            style={"marginBottom": "50px"},
        ),
        html.Hr(),
        # PARTIE 2 : COMPETENCE / COMPOSANTES ESSENTIELLES
        html.H3(
            "Compétences et Composantes essentielles",
            style={"marginTop": "30px", "marginBottom": "20px"},
        ),
        html.Div(
            [
                html.Label("Choisir une compétence :"),
                dcc.Dropdown(
                    id="competence-ce-dropdown",
                    placeholder="Choisir une compétence",
                    clearable=False,
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="competence-ce-graph")],
                    style={"width": "60%", "display": "inline-block", "verticalAlign": "top"},
                ),
                html.Div(
                    [html.Div(id="competence_ce")],
                    style={
                        "width": "38%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "paddingLeft": "20px",
                        "maxHeight": "520px",
                        "overflowY": "auto",
                    },
                ),
            ]
        ),
    ]
)
