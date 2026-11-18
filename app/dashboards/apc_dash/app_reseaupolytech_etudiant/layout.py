"""Layout de la vue Réseau Polytech étudiant."""

from dash import dcc, html
import dash_leaflet as dl

COLORS = {
    "primary": "#0056b3",
    "background": "#f4f7f6",
    "card": "#ffffff",
    "shadow": "0 4px 12px rgba(0,0,0,0.08)",
}


def create_app_header():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(className="header-logo-icon"),
                            html.Div(
                                [
                                    html.H1(
                                        "Learnagement - Tableau de bord", className="header-title"
                                    ),
                                    html.P(
                                        "Explorez les formations, compétences et débouchés des écoles Polytech",
                                        className="header-subtitle",
                                    ),
                                ]
                            ),
                        ],
                        className="header-logo",
                    ),
                ],
                className="header-content",
            ),
        ],
        className="app-header",
        style={
            "position": "sticky",
            "top": "0",
            "zIndex": "9999",
            "backgroundColor": "white",
            "width": "100%",
        },
    )


polytech_analysis_layout = html.Div(
    style={"backgroundColor": COLORS["background"], "minHeight": "100vh"},
    children=[
        dcc.Store(id="selected-school-store", data="ALL"),
        # ── Page Réseau Polytech ──────────────────────────────────────────────
        html.Div(
            id="page-reseau",
            children=[
                html.Div(
                    style={"padding": "24px"},
                    children=[
                        html.Div(
                            style={
                                "backgroundColor": COLORS["card"],
                                "padding": "15px",
                                "borderRadius": "15px",
                                "boxShadow": COLORS["shadow"],
                                "marginBottom": "20px",
                            },
                            children=[
                                html.H3(
                                    "Localisation des écoles",
                                    style={
                                        "margin": "0 0 12px",
                                        "fontSize": "16px",
                                        "fontWeight": "500",
                                    },
                                ),
                                dl.Map(
                                    [dl.TileLayer(), dl.LayerGroup(id="layer-markers")],
                                    center=[46.5, 2.5],
                                    zoom=6,
                                    style={"height": "55vh", "borderRadius": "10px"},
                                ),
                                html.Div(
                                    "Cliquez sur une école pour explorer ses formations",
                                    style={
                                        "fontSize": "12px",
                                        "color": "#bbb",
                                        "textAlign": "center",
                                        "marginTop": "8px",
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="bloc-filieres",
                            style={"display": "none"},
                            children=[
                                html.Div(
                                    style={
                                        "backgroundColor": COLORS["card"],
                                        "padding": "20px 25px",
                                        "borderRadius": "15px",
                                        "boxShadow": COLORS["shadow"],
                                        "marginBottom": "20px",
                                    },
                                    children=[
                                        html.Div(
                                            id="breadcrumb",
                                            style={
                                                "fontSize": "14px",
                                                "marginBottom": "16px",
                                                "paddingBottom": "12px",
                                                "borderBottom": "1px solid #f0f0f0",
                                            },
                                        ),
                                        html.Div(
                                            "① Choisissez une filière",
                                            style={
                                                "fontSize": "10px",
                                                "color": "#bbb",
                                                "fontWeight": "600",
                                                "textTransform": "uppercase",
                                                "letterSpacing": "1px",
                                                "marginBottom": "12px",
                                            },
                                        ),
                                        html.Div(
                                            id="col-filieres",
                                            style={
                                                "display": "flex",
                                                "flexWrap": "wrap",
                                                "gap": "8px",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            id="bloc-detail",
                            style={"display": "none"},
                            children=[
                                html.Div(
                                    style={
                                        "backgroundColor": COLORS["card"],
                                        "padding": "20px 25px",
                                        "borderRadius": "15px",
                                        "boxShadow": COLORS["shadow"],
                                        "marginBottom": "20px",
                                    },
                                    children=[
                                        html.Div(
                                            id="detail-breadcrumb",
                                            style={
                                                "fontSize": "14px",
                                                "marginBottom": "20px",
                                                "paddingBottom": "12px",
                                                "borderBottom": "1px solid #f0f0f0",
                                            },
                                        ),
                                        html.Div(
                                            style={"display": "flex", "gap": "30px"},
                                            children=[
                                                html.Div(
                                                    style={"flex": "1", "minWidth": "0"},
                                                    children=[
                                                        html.Div(
                                                            "② Compétences",
                                                            style={
                                                                "fontSize": "10px",
                                                                "color": "#bbb",
                                                                "fontWeight": "600",
                                                                "textTransform": "uppercase",
                                                                "letterSpacing": "1px",
                                                                "marginBottom": "12px",
                                                            },
                                                        ),
                                                        html.Ul(
                                                            id="liste-competences",
                                                            style={
                                                                "paddingLeft": "18px",
                                                                "margin": "0",
                                                                "fontSize": "13px",
                                                                "lineHeight": "1.8",
                                                            },
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    style={
                                                        "width": "1px",
                                                        "backgroundColor": "#f0f0f0",
                                                        "flexShrink": "0",
                                                    }
                                                ),
                                                html.Div(
                                                    style={"flex": "1", "minWidth": "0"},
                                                    children=[
                                                        html.Div(
                                                            "③ Débouchés & Secteurs",
                                                            style={
                                                                "fontSize": "10px",
                                                                "color": "#bbb",
                                                                "fontWeight": "600",
                                                                "textTransform": "uppercase",
                                                                "letterSpacing": "1px",
                                                                "marginBottom": "12px",
                                                            },
                                                        ),
                                                        html.Div(
                                                            id="col-metiers",
                                                            style={
                                                                "display": "flex",
                                                                "flexWrap": "wrap",
                                                                "gap": "6px",
                                                            },
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # ── Page Polytech Annecy ──────────────────────────────────────────────
        html.Div(
            id="page-annecy",
            style={"display": "none"},
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "height": "60vh",
                        "gap": "16px",
                    },
                    children=[
                        html.Div("🚧", style={"fontSize": "48px"}),
                        html.H2(
                            "Polytech Annecy",
                            style={
                                "fontSize": "22px",
                                "fontWeight": "500",
                                "color": "#333",
                                "margin": "0",
                            },
                        ),
                        html.P(
                            "Cette section est en cours de construction.",
                            style={"color": "#aaa", "fontSize": "14px", "margin": "0"},
                        ),
                    ],
                )
            ],
        ),
    ],
)
