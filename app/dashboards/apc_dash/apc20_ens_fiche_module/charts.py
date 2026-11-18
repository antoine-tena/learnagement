"""Construction des cartes, graphiques et listes d'AC pour la fiche module."""

from dash import html
import plotly.express as px
import plotly.graph_objects as go

from apc_dash.apc20_layout import COLORS, get_competence_color

from .layout import _LIEN_COLORS


def _info_card(label, value, color):
    return html.Div(
        [
            html.Div(label, style={"fontSize": "11px", "color": "#6B7280", "marginBottom": "4px"}),
            html.Div(str(value), style={"fontSize": "22px", "fontWeight": "700", "color": color}),
        ],
        style={
            "backgroundColor": "white",
            "padding": "14px",
            "borderRadius": "8px",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
            "borderLeft": f"3px solid {color}",
            "textAlign": "center",
        },
    )


def build_info_cards(df_mod, df_modules, module_id: float):
    mod_row = df_modules[df_modules["id_module"] == module_id]
    if not mod_row.empty:
        r = mod_row.iloc[0]
        ects = r.get("ECTS", "—")
        sem = r.get("id_semestre", "—")
        hcm = float(r.get("hCM", 0) or 0)
        htd = float(r.get("hTD", 0) or 0)
        htp = float(r.get("hTP", 0) or 0)
        total_h: float | str = hcm + htd + htp
    else:
        ects, sem, total_h = "—", "—", "—"

    return [
        _info_card("ECTS", ects, COLORS["primary"]),
        _info_card("Semestre", f"S{sem}", COLORS["success"]),
        _info_card(
            "Heures", f"{total_h:.0f}h" if isinstance(total_h, float) else "—", COLORS["warning"]
        ),
        _info_card("AC couverts", df_mod["id_apprentissage_critique"].nunique(), COLORS["danger"]),
    ]


def build_donut_figure(df_mod):
    lien_counts = df_mod["type_lien"].value_counts()
    donut_colors = [_LIEN_COLORS.get(lien, "#999") for lien in lien_counts.index]
    fig_donut = go.Figure(
        data=[
            go.Pie(
                labels=lien_counts.index.tolist(),
                values=lien_counts.values.tolist(),
                hole=0.55,
                marker_colors=donut_colors,
                textinfo="label+percent",
                insidetextorientation="radial",
            )
        ]
    )
    fig_donut.update_layout(
        title=dict(
            text="Répartition des types de lien", x=0.5, xanchor="center", font=dict(size=13)
        ),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        showlegend=False,
        font=dict(family="Inter, sans-serif"),
    )
    return fig_donut


def build_bar_figure(df_mod):
    df_bar = (
        df_mod.groupby("competence_label")["id_apprentissage_critique"]
        .nunique()
        .reset_index(name="nb_ac")
    )
    fig_bar = px.bar(
        df_bar,
        x="competence_label",
        y="nb_ac",
        text="nb_ac",
        color="competence_label",
        color_discrete_map={c: get_competence_color(c) for c in df_bar["competence_label"]},
        title="AC couverts par compétence",
    )
    fig_bar.update_traces(textposition="outside", cliponaxis=False)
    fig_bar.update_layout(
        showlegend=False,
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="",
        yaxis_title="Nombre d'AC",
        font=dict(family="Inter, sans-serif"),
    )
    return fig_bar


def build_ac_list(df_mod):
    sections = []
    for comp in sorted(df_mod["competence_label"].dropna().unique()):
        df_c = df_mod[df_mod["competence_label"] == comp].drop_duplicates(
            "id_apprentissage_critique"
        )
        comp_color = get_competence_color(comp)

        rows = []
        for _, row in df_c.sort_values(["niveau", "libelle_apprentissage"]).iterrows():
            lien = row.get("type_lien", "")
            lc = _LIEN_COLORS.get(lien, "#9CA3AF")
            rows.append(
                html.Div(
                    [
                        html.Span(
                            f"N{int(row['niveau'])}",
                            style={
                                "fontSize": "11px",
                                "fontWeight": "600",
                                "backgroundColor": "#E5E7EB",
                                "borderRadius": "4px",
                                "padding": "2px 6px",
                                "marginRight": "8px",
                                "flexShrink": "0",
                            },
                        ),
                        html.Span(
                            row["libelle_apprentissage"],
                            style={"flex": "1", "fontSize": "13px"},
                        ),
                        html.Span(
                            lien,
                            style={
                                "fontSize": "11px",
                                "fontWeight": "600",
                                "color": lc,
                                "backgroundColor": lc + "20",
                                "borderRadius": "4px",
                                "padding": "2px 8px",
                                "flexShrink": "0",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "8px",
                        "padding": "8px 10px",
                        "borderRadius": "6px",
                        "backgroundColor": "#F9FAFB",
                        "marginBottom": "4px",
                    },
                )
            )

        sections.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                style={
                                    "width": "12px",
                                    "height": "12px",
                                    "borderRadius": "3px",
                                    "backgroundColor": comp_color,
                                    "marginRight": "8px",
                                }
                            ),
                            html.Span(comp, style={"fontWeight": "700", "fontSize": "14px"}),
                            html.Span(
                                f"  {len(rows)} AC",
                                style={
                                    "fontSize": "12px",
                                    "color": "#6B7280",
                                    "marginLeft": "8px",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "marginBottom": "10px",
                        },
                    ),
                    html.Div(rows),
                ],
                style={"marginBottom": "16px"},
            )
        )

    return html.Div(
        [
            html.H4(
                "Apprentissages critiques couverts",
                style={"margin": "0 0 16px 0", "fontSize": "15px"},
            ),
            html.Div(sections),
        ]
    )
