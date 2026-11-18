"""Layout et figures par défaut de la vue Orientation par métier."""

from dash import dcc, html
import plotly.graph_objects as go

COLOR_MAP = {
    "COMP_IDU1": "#FF4E3A",
    "COMP_IDU2": "#F39C3D",
    "COMP_IDU3": "#3F7EE8",
    "COMP_IDU4": "#1FB985",
}


def empty_figure(message="Chargement des données..."):
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 16, "color": "#666"},
            }
        ],
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def default_ac_panel():
    return html.Div(
        [
            html.H4(
                "Apprentissages critiques par semestre",
                style={"fontWeight": "bold", "marginBottom": "10px"},
            ),
            html.P(
                "Sélectionnez un semestre dans le graphique pour afficher les apprentissages critiques.",
                style={"margin": "0", "color": "#555"},
            ),
        ]
    )


apc20_metier_orientation_layout = html.Div(
    [
        dcc.Store(id="metier-ac-store"),
        html.H2("Orientation par métier", style={"marginBottom": "10px"}),
        html.P(
            "Choisissez un métier pour découvrir les compétences clés, "
            "les apprentissages critiques et leur progression par semestre.",
            style={"marginBottom": "25px"},
        ),
        html.Div(
            [
                html.Label("MÉTIER", style={"fontWeight": "bold", "marginBottom": "8px"}),
                dcc.Dropdown(
                    id="metier-dropdown", placeholder="Choisir un métier", clearable=False
                ),
            ],
            style={"marginBottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(
                            id="metier-competence-graph",
                            figure=empty_figure("Chargement des compétences..."),
                        )
                    ],
                    style={"width": "49%", "display": "inline-block", "verticalAlign": "top"},
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="metier-semestre-graph",
                            figure=empty_figure("Chargement des semestres..."),
                        )
                    ],
                    style={
                        "width": "49%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "marginLeft": "2%",
                    },
                ),
            ],
            style={"marginBottom": "30px"},
        ),
        html.Div(
            id="metier-semestre-ac-list",
            children=default_ac_panel(),
            style={
                "padding": "20px",
                "border": "1px solid #d9d9d9",
                "borderRadius": "10px",
                "backgroundColor": "#fafafa",
            },
        ),
    ]
)
