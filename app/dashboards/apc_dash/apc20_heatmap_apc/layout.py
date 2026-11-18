from dash import dcc, html

from .queries import (
    COLORS,
    KNOWN_COMPETENCES,
    KNOWN_NIVEAUX,
    KNOWN_TYPES_LIEN,
    _empty_fig,
)

heatmap_apc_layout = html.Div(
    [
        # Stores
        dcc.Store(id="heatmap-apc-raw-store"),
        dcc.Store(id="heatmap-apc-filtered-store"),
        dcc.Store(id="heatmap-apc-drill-level", data="global"),
        dcc.Store(id="heatmap-apc-selected-niveau", data=None),
        dcc.Store(id="heatmap-apc-selected-module", data=None),
        # Header
        html.Div(
            [
                html.H1("Heatmap APC — Mon parcours", style={"margin": "0", "fontSize": "22px"}),
                html.P(
                    "Exploration interactive : cliquez sur un niveau pour descendre dans les modules, "
                    "puis sur un module pour voir les apprentissages critiques.",
                    style={"margin": "4px 0 0 0", "color": "#6B7280", "fontSize": "14px"},
                ),
            ],
            style={
                "backgroundColor": "white",
                "padding": "16px 24px",
                "borderBottom": "1px solid #E5E7EB",
                "position": "sticky",
                "top": "0",
                "zIndex": "999",
            },
        ),
        # Body : sidebar + contenu principal
        html.Div(
            [
                # Sidebar filtres
                html.Div(
                    [
                        html.H3(
                            "Filtres",
                            style={"marginBottom": "16px", "fontSize": "16px", "fontWeight": "600"},
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Niveaux", style={"fontWeight": "500", "fontSize": "13px"}
                                ),
                                dcc.Dropdown(
                                    id="heatmap-apc-niveau-filter",
                                    options=[
                                        {"label": f"Niveau {n}", "value": n} for n in KNOWN_NIVEAUX
                                    ],
                                    value=KNOWN_NIVEAUX,
                                    multi=True,
                                    placeholder="Tous les niveaux",
                                ),
                            ],
                            style={"marginBottom": "14px"},
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Compétences", style={"fontWeight": "500", "fontSize": "13px"}
                                ),
                                dcc.Dropdown(
                                    id="heatmap-apc-comp-filter",
                                    options=[{"label": c, "value": c} for c in KNOWN_COMPETENCES],
                                    value=KNOWN_COMPETENCES,
                                    multi=True,
                                    placeholder="Toutes les compétences",
                                ),
                            ],
                            style={"marginBottom": "14px"},
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Types de lien", style={"fontWeight": "500", "fontSize": "13px"}
                                ),
                                dcc.Checklist(
                                    id="heatmap-apc-lien-filter",
                                    options=[{"label": t, "value": t} for t in KNOWN_TYPES_LIEN],
                                    value=KNOWN_TYPES_LIEN,
                                    labelStyle={"display": "block", "marginBottom": "4px"},
                                ),
                            ],
                            style={"marginBottom": "14px"},
                        ),
                        html.Button(
                            "↻ Réinitialiser",
                            id="heatmap-apc-reset-filters",
                            n_clicks=0,
                            style={
                                "width": "100%",
                                "padding": "8px",
                                "cursor": "pointer",
                                "backgroundColor": "#F3F4F6",
                                "border": "1px solid #D1D5DB",
                                "borderRadius": "6px",
                            },
                        ),
                        html.Div(
                            id="heatmap-apc-filter-status",
                            style={"marginTop": "8px", "fontSize": "12px", "color": "#6B7280"},
                        ),
                    ],
                    style={
                        "width": "240px",
                        "flexShrink": "0",
                        "padding": "20px",
                        "backgroundColor": "white",
                        "borderRight": "1px solid #E5E7EB",
                        "minHeight": "calc(100vh - 80px)",
                    },
                ),
                # Contenu principal
                html.Div(
                    [
                        # Breadcrumb + boutons navigation
                        html.Div(
                            [
                                html.Div(id="heatmap-apc-breadcrumb", style={"flex": "1"}),
                                html.Div(
                                    [
                                        html.Button(
                                            "Vue globale",
                                            id="heatmap-apc-btn-global",
                                            n_clicks=0,
                                            style={
                                                "padding": "6px 14px",
                                                "cursor": "pointer",
                                                "backgroundColor": COLORS["primary"],
                                                "color": "white",
                                                "border": "none",
                                                "borderRadius": "6px",
                                                "marginRight": "8px",
                                            },
                                        ),
                                        html.Button(
                                            "← Retour",
                                            id="heatmap-apc-btn-back",
                                            n_clicks=0,
                                            style={
                                                "padding": "6px 14px",
                                                "cursor": "pointer",
                                                "backgroundColor": "white",
                                                "color": "#374151",
                                                "border": "1px solid #D1D5DB",
                                                "borderRadius": "6px",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "marginBottom": "12px",
                                "gap": "12px",
                            },
                        ),
                        # Graphe heatmap drill-down
                        html.Div(
                            dcc.Graph(
                                id="heatmap-apc-drilldown",
                                figure=_empty_fig(),
                                config={"displayModeBar": True, "displaylogo": False},
                                style={"width": "100%"},
                            ),
                            style={
                                "backgroundColor": "white",
                                "borderRadius": "10px",
                                "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
                                "padding": "12px",
                            },
                        ),
                    ],
                    style={"flex": "1", "padding": "20px", "overflow": "auto"},
                ),
            ],
            style={"display": "flex", "minHeight": "calc(100vh - 80px)"},
        ),
    ],
    style={"fontFamily": "Inter, sans-serif", "backgroundColor": "#F9FAFB"},
)
