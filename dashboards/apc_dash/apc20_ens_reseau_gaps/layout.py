from dash import dcc, html

from ..apc20_layout import COLORS, KNOWN_COMPETENCES, empty_fig

reseau_gaps_content = html.Div(
    [
        dcc.Store(id="reseau-selected-node", data=None),
        # ── Section Réseau ────────────────────────────────────────
        html.Div(
            [
                html.H3(
                    "Réseau de modules",
                    style={"margin": "0 0 4px 0", "fontSize": "16px", "fontWeight": "700"},
                ),
                html.P(
                    "Deux modules sont reliés s'ils partagent au moins un apprentissage critique. "
                    "La taille du nœud reflète le nombre d'AC couverts, "
                    "la couleur indique la compétence dominante. "
                    "Cliquez sur un nœud pour zoomer sur ses connexions.",
                    style={"margin": "0 0 14px 0", "color": "#6B7280", "fontSize": "13px"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(
                                    "Filtrer par compétence",
                                    style={
                                        "fontWeight": "500",
                                        "fontSize": "13px",
                                        "marginBottom": "6px",
                                        "display": "block",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="reseau-comp-filter",
                                    options=[{"label": c, "value": c} for c in KNOWN_COMPETENCES],
                                    value=KNOWN_COMPETENCES,
                                    multi=True,
                                    placeholder="Toutes les compétences",
                                ),
                            ],
                            style={"flex": "1"},
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Rechercher un module",
                                    style={
                                        "fontWeight": "500",
                                        "fontSize": "13px",
                                        "marginBottom": "6px",
                                        "display": "block",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="reseau-search-module",
                                    options=[],
                                    value=None,
                                    searchable=True,
                                    clearable=True,
                                    placeholder="Tapez le nom ou code d'un module...",
                                ),
                            ],
                            style={"flex": "1"},
                        ),
                    ],
                    style={"display": "flex", "gap": "16px", "marginBottom": "14px"},
                ),
                # Graphe + bouton reset superposé
                html.Div(
                    [
                        dcc.Graph(
                            id="reseau-graph",
                            figure=empty_fig(),
                            config={"displayModeBar": True, "displaylogo": False},
                            style={"height": "560px"},
                        ),
                        html.Button(
                            [
                                html.I(
                                    className="fa-solid fa-arrow-rotate-left",
                                    style={"marginRight": "6px"},
                                ),
                                "Retour vue globale",
                            ],
                            id="reseau-reset-btn",
                            n_clicks=0,
                            style={
                                "display": "none",
                                "position": "absolute",
                                "top": "14px",
                                "left": "14px",
                                "zIndex": "10",
                                "backgroundColor": COLORS["primary"],
                                "color": "white",
                                "border": "none",
                                "borderRadius": "6px",
                                "padding": "7px 13px",
                                "fontSize": "13px",
                                "fontWeight": "600",
                                "cursor": "pointer",
                                "boxShadow": "0 2px 6px rgba(0,0,0,0.2)",
                                "fontFamily": "Inter, sans-serif",
                            },
                        ),
                    ],
                    style={
                        "position": "relative",
                        "backgroundColor": "white",
                        "borderRadius": "10px",
                        "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
                        "padding": "12px",
                    },
                ),
            ],
            style={"marginBottom": "28px"},
        ),
        # ── Section Gaps ──────────────────────────────────────────
        html.Div(
            [
                html.H3(
                    "Analyse des trous APC",
                    style={"margin": "0 0 4px 0", "fontSize": "16px", "fontWeight": "700"},
                ),
                html.P(
                    "Les AC sans module 'Requis' risquent de ne pas être réellement maîtrisés. "
                    "Les modules sans AC 'Requis' ont un ancrage APC faible.",
                    style={"margin": "0 0 14px 0", "color": "#6B7280", "fontSize": "13px"},
                ),
                html.Div(
                    [
                        html.Div(id="gaps-ac-orphans", style={"flex": "1"}),
                        html.Div(id="gaps-module-orphans", style={"flex": "1"}),
                    ],
                    style={"display": "flex", "gap": "16px"},
                ),
            ],
        ),
    ],
    style={"padding": "20px"},
)
