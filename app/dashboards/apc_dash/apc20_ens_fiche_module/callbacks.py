"""Callbacks Dash de la fiche APC d'un module."""

from io import StringIO

from dash import Input, Output, State, html
import pandas as pd

from apc_dash.apc20_layout import empty_fig

from .charts import build_ac_list, build_bar_figure, build_donut_figure, build_info_cards


def register_callbacks(app):
    @app.callback(
        Output("fiche-module-select", "options"),
        Input("apc-ens-raw-store", "data"),
        prevent_initial_call=False,
    )
    def populate_module_options(raw_data):
        if raw_data is None:
            return []
        module_names = raw_data.get("module_names", {})
        opts = []
        for k, v in module_names.items():
            try:
                if float(k) == 0:
                    continue
            except ValueError, TypeError:
                continue
            opts.append({"label": v, "value": k})
        return sorted(opts, key=lambda x: x["label"])

    @app.callback(
        Output("fiche-info-cards", "children"),
        Output("fiche-donut-chart", "figure"),
        Output("fiche-bar-chart", "figure"),
        Output("fiche-ac-list", "children"),
        Input("fiche-module-select", "value"),
        State("apc-ens-raw-store", "data"),
        prevent_initial_call=False,
    )
    def update_fiche(module_id_str, raw_data):
        _empty = empty_fig("Sélectionnez un module")
        _placeholder = html.P(
            "Sélectionnez un module pour afficher ses apprentissages critiques.",
            style={"color": "#6B7280"},
        )

        if not module_id_str or raw_data is None:
            return [], _empty, _empty, _placeholder

        df_main = pd.read_json(StringIO(raw_data["df_main"]), orient="split")
        df_modules = pd.read_json(StringIO(raw_data["df_modules"]), orient="split")

        try:
            module_id = float(module_id_str)
        except ValueError, TypeError:
            return [], empty_fig("Module introuvable"), _empty, html.P("Module introuvable.")

        df_mod = df_main[df_main["id_module"] == module_id].copy()
        if df_mod.empty:
            return (
                [],
                empty_fig("Aucun AC pour ce module"),
                _empty,
                html.P("Aucun apprentissage critique associé."),
            )

        cards = build_info_cards(df_mod, df_modules, module_id)
        fig_donut = build_donut_figure(df_mod)
        fig_bar = build_bar_figure(df_mod)
        ac_list = build_ac_list(df_mod)

        return cards, fig_donut, fig_bar, ac_list
