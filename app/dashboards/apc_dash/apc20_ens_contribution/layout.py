"""Layout et constantes de la vue Ma contribution APC personnelle."""

from dash import dcc, html

from apc_dash.apc20_layout import empty_fig

_LIEN_COLORS = {
    "Requis": "#EF4444",
    "Recommandé": "#F59E0B",
    "Complémentaire": "#10B981",
}

contribution_content = html.Div(
    [
        # Sélection des modules
        html.Div(
            [
                html.Label(
                    "Mes modules",
                    style={"fontWeight": "600", "marginBottom": "6px", "display": "block"},
                ),
                html.P(
                    "Sélectionnez les modules dont vous êtes responsable pour visualiser votre contribution APC.",
                    style={"margin": "0 0 10px 0", "color": "#6B7280", "fontSize": "13px"},
                ),
                dcc.Dropdown(
                    id="contribution-modules-select",
                    options=[],
                    value=[],
                    multi=True,
                    placeholder="Sélectionner vos modules...",
                ),
            ],
            style={"marginBottom": "20px"},
        ),
        # Stat cards
        html.Div(
            id="contribution-stats-row",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                "gap": "12px",
                "marginBottom": "20px",
            },
        ),
        # Radar + Histogramme
        html.Div(
            [
                html.Div(
                    dcc.Graph(
                        id="contribution-radar",
                        figure=empty_fig("Sélectionnez vos modules"),
                        config={"displayModeBar": False},
                    ),
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "10px",
                        "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
                        "padding": "12px",
                        "flex": "0 0 400px",
                    },
                ),
                html.Div(
                    dcc.Graph(
                        id="contribution-bar",
                        figure=empty_fig("Sélectionnez vos modules"),
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
            id="contribution-ac-list",
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
