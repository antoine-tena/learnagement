"""Layout et constantes de la fiche APC d'un module."""

from dash import dcc, html

from apc_dash.apc20_layout import empty_fig

_LIEN_COLORS = {
    "Requis": "#EF4444",
    "Recommandé": "#F59E0B",
    "Complémentaire": "#10B981",
}

fiche_module_content = html.Div(
    [
        # Sélection du module
        html.Div(
            [
                html.Label(
                    "Module",
                    style={"fontWeight": "600", "marginBottom": "8px", "display": "block"},
                ),
                dcc.Dropdown(
                    id="fiche-module-select",
                    options=[],
                    value=None,
                    placeholder="Choisir un module...",
                    clearable=True,
                    style={"maxWidth": "560px"},
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        # Cartes info (remplies par callback)
        html.Div(
            id="fiche-info-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
                "gap": "12px",
                "marginBottom": "20px",
            },
        ),
        # Donut + Histogramme
        html.Div(
            [
                html.Div(
                    dcc.Graph(
                        id="fiche-donut-chart",
                        figure=empty_fig(),
                        config={"displayModeBar": False},
                    ),
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "10px",
                        "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
                        "padding": "12px",
                        "flex": "0 0 320px",
                    },
                ),
                html.Div(
                    dcc.Graph(
                        id="fiche-bar-chart",
                        figure=empty_fig(),
                        config={"displayModeBar": False},
                    ),
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "10px",
                        "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
                        "padding": "12px",
                        "flex": "1",
                    },
                ),
            ],
            style={"display": "flex", "gap": "16px", "marginBottom": "20px"},
        ),
        # Liste des AC
        html.Div(
            id="fiche-ac-list",
            style={
                "backgroundColor": "white",
                "borderRadius": "10px",
                "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
                "padding": "20px",
            },
        ),
    ],
    style={"padding": "20px"},
)
