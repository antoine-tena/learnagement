from io import StringIO

import pandas as pd
from dash import html

from ..apc20_layout import get_competence_color


def build_gaps_panels(raw_data):
    _na = html.P("Données non disponibles", style={"color": "#6B7280"})
    if raw_data is None:
        return _na, _na

    df_main = pd.read_json(StringIO(raw_data["df_main"]), orient="split")
    module_names = raw_data.get("module_names", {})

    def _badge(text, color):
        return html.Span(
            text,
            style={
                "fontSize": "11px",
                "fontWeight": "600",
                "color": color,
                "backgroundColor": color + "22",
                "borderRadius": "4px",
                "padding": "2px 7px",
                "marginRight": "6px",
            },
        )

    ac_with_requis = set(
        df_main[df_main["type_lien"] == "Requis"]["id_apprentissage_critique"].unique()
    )
    all_acs = df_main[
        ["id_apprentissage_critique", "libelle_apprentissage", "competence_label", "niveau"]
    ].drop_duplicates("id_apprentissage_critique")
    ac_orphans = all_acs[~all_acs["id_apprentissage_critique"].isin(ac_with_requis)]

    ac_rows = []
    for _, row in ac_orphans.sort_values(
        ["competence_label", "niveau", "libelle_apprentissage"]
    ).iterrows():
        ac_rows.append(
            html.Div(
                [
                    _badge(
                        str(row["competence_label"]),
                        get_competence_color(str(row["competence_label"])),
                    ),
                    _badge(f"N{int(row['niveau'])}", "#6B7280"),
                    html.Span(str(row["libelle_apprentissage"]), style={"fontSize": "13px"}),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "flexWrap": "wrap",
                    "padding": "7px 10px",
                    "borderRadius": "6px",
                    "backgroundColor": "#FEF2F2",
                    "marginBottom": "4px",
                    "borderLeft": "3px solid #EF4444",
                },
            )
        )

    ac_panel = html.Div(
        [
            html.Div(
                [
                    html.H4(
                        "AC sans module 'Requis'",
                        style={"margin": "0", "fontSize": "14px", "fontWeight": "700"},
                    ),
                    html.Span(
                        f"{len(ac_orphans)} / {len(all_acs)} AC",
                        style={"fontSize": "12px", "color": "#EF4444", "fontWeight": "600"},
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "marginBottom": "12px",
                },
            ),
            html.Div(
                ac_rows
                or [html.P("Aucun trou détecté.", style={"color": "#10B981", "fontSize": "13px"})],
                style={"maxHeight": "360px", "overflowY": "auto"},
            ),
        ],
        style={
            "backgroundColor": "white",
            "borderRadius": "10px",
            "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
            "padding": "16px",
        },
    )

    mod_with_requis = set(df_main[df_main["type_lien"] == "Requis"]["id_module"].unique())
    all_modules = df_main[df_main["id_module"] != 0]["id_module"].unique()
    mod_orphans = [m for m in all_modules if m not in mod_with_requis]

    mod_rows = []
    for m in sorted(mod_orphans):
        name = module_names.get(str(int(m)), module_names.get(str(m), f"Module {m}"))
        mod_rows.append(
            html.Div(
                html.Span(str(name), style={"fontSize": "13px"}),
                style={
                    "padding": "7px 10px",
                    "borderRadius": "6px",
                    "backgroundColor": "#FFFBEB",
                    "marginBottom": "4px",
                    "borderLeft": "3px solid #F59E0B",
                },
            )
        )

    mod_panel = html.Div(
        [
            html.Div(
                [
                    html.H4(
                        "Modules sans AC 'Requis'",
                        style={"margin": "0", "fontSize": "14px", "fontWeight": "700"},
                    ),
                    html.Span(
                        f"{len(mod_orphans)} / {len(all_modules)} modules",
                        style={"fontSize": "12px", "color": "#F59E0B", "fontWeight": "600"},
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "marginBottom": "12px",
                },
            ),
            html.Div(
                mod_rows
                or [
                    html.P(
                        "Tous les modules ont au moins un AC Requis.",
                        style={"color": "#10B981", "fontSize": "13px"},
                    )
                ],
                style={"maxHeight": "360px", "overflowY": "auto"},
            ),
        ],
        style={
            "backgroundColor": "white",
            "borderRadius": "10px",
            "boxShadow": "0 1px 4px rgba(0,0,0,0.08)",
            "padding": "16px",
        },
    )

    return ac_panel, mod_panel
