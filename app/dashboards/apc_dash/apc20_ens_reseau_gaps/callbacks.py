from dash import Input, Output, callback_context

from ..apc20_layout import COLORS
from .queries import build_reseau_figure
from .queries_gaps import build_gaps_panels


def register_callbacks(app):
    # ── Peuplement du dropdown de recherche ──────────────────────
    @app.callback(
        Output("reseau-search-module", "options"),
        Input("apc-ens-raw-store", "data"),
        prevent_initial_call=False,
    )
    def populate_search_options(raw_data):
        if not raw_data:
            return []
        module_names = raw_data.get("module_names", {})
        return [
            {"label": label, "value": mid}
            for mid, label in sorted(module_names.items(), key=lambda x: x[1])
            if mid != "0"
        ]

    # ── Vidage du dropdown sur reset ou changement de filtre ─────
    @app.callback(
        Output("reseau-search-module", "value"),
        Input("reseau-reset-btn", "n_clicks"),
        Input("reseau-comp-filter", "value"),
        prevent_initial_call=True,
    )
    def clear_search(_reset, _filter):
        return None

    # ── Mise à jour du nœud sélectionné (clic, recherche ou reset) ──
    @app.callback(
        Output("reseau-selected-node", "data"),
        Input("reseau-graph", "clickData"),
        Input("reseau-reset-btn", "n_clicks"),
        Input("reseau-comp-filter", "value"),
        Input("reseau-search-module", "value"),
        prevent_initial_call=True,
    )
    def update_selected_node(click_data, _reset, _filter, search_value):
        ctx = callback_context
        triggered = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

        if triggered in ("reseau-reset-btn", "reseau-comp-filter"):
            return None

        if triggered == "reseau-search-module":
            if search_value is not None:
                try:
                    return float(search_value)
                except ValueError, TypeError:
                    pass
            return None

        if triggered == "reseau-graph" and click_data and click_data.get("points"):
            pt = click_data["points"][0]
            cd = pt.get("customdata")
            if cd is not None:
                try:
                    return float(cd)
                except ValueError, TypeError:
                    pass
        return None

    # ── Visibilité du bouton reset ────────────────────────────────
    @app.callback(
        Output("reseau-reset-btn", "style"),
        Input("reseau-selected-node", "data"),
        prevent_initial_call=False,
    )
    def toggle_reset_btn(selected):
        base = {
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
        }
        base["display"] = "flex" if selected is not None else "none"
        base["alignItems"] = "center"
        return base

    # ── Viz 3 : Réseau de modules ─────────────────────────────────
    @app.callback(
        Output("reseau-graph", "figure"),
        Input("reseau-comp-filter", "value"),
        Input("apc-ens-raw-store", "data"),
        Input("reseau-selected-node", "data"),
        prevent_initial_call=False,
    )
    def update_reseau(competences, raw_data, clicked_mod):
        return build_reseau_figure(competences, raw_data, clicked_mod)

    # ── Viz 4 : Analyse des trous ─────────────────────────────────
    @app.callback(
        Output("gaps-ac-orphans", "children"),
        Output("gaps-module-orphans", "children"),
        Input("apc-ens-raw-store", "data"),
        prevent_initial_call=False,
    )
    def update_gaps(raw_data):
        return build_gaps_panels(raw_data)
