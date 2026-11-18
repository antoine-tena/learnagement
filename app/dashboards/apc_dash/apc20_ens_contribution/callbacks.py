"""Callbacks Dash de la vue Ma contribution APC personnelle."""

from io import StringIO

from dash import Input, Output, State, html
import pandas as pd

from apc_dash.apc20_layout import empty_fig

from .charts import build_ac_list, build_bar_figure, build_radar_figure, build_stats_cards


def register_callbacks(app):
    @app.callback(
        Output("contribution-modules-select", "options"),
        Input("apc-ens-raw-store", "data"),
        prevent_initial_call=False,
    )
    def populate_contribution_options(raw_data):
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
        Output("contribution-stats-row", "children"),
        Output("contribution-radar", "figure"),
        Output("contribution-bar", "figure"),
        Output("contribution-ac-list", "children"),
        Input("contribution-modules-select", "value"),
        State("apc-ens-raw-store", "data"),
        prevent_initial_call=False,
    )
    def update_contribution(selected_strs, raw_data):
        _empty = empty_fig("Sélectionnez vos modules")
        _hint = html.P(
            "Sélectionnez vos modules pour voir votre contribution.", style={"color": "#6B7280"}
        )

        if not selected_strs or raw_data is None:
            return [], _empty, _empty, _hint

        df_main = pd.read_json(StringIO(raw_data["df_main"]), orient="split")

        try:
            selected_ids = [float(s) for s in selected_strs]
        except ValueError, TypeError:
            return [], _empty, _empty, html.P("Erreur de sélection.")

        df_mine = df_main[df_main["id_module"].isin(selected_ids)].copy()
        if df_mine.empty:
            return (
                [],
                empty_fig("Aucun AC pour les modules sélectionnés"),
                _empty,
                html.P("Aucun AC trouvé."),
            )

        stats = build_stats_cards(df_mine, df_main, len(selected_ids))
        fig_radar = build_radar_figure(df_mine, df_main)
        fig_bar = build_bar_figure(df_mine, raw_data.get("module_names", {}))
        ac_list = build_ac_list(df_mine)

        return stats, fig_radar, fig_bar, ac_list
