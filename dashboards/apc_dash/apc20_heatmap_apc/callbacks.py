import logging
from io import StringIO

import dash
import pandas as pd
from dash import Input, Output, State, html

from ..apc20_heatmap_apc_tools import (
    get_apc_ac_modules,
    get_apc_apprentissages,
    get_apc_competences,
    get_apc_composantes,
    get_apc_modules,
    get_apc_niveaux,
)
from .queries import (
    _empty_fig,
    compute_competency_counts_per_module,
    create_heatmap_for_global,
    create_heatmap_for_module,
    create_heatmap_for_niveau,
    parse_competencies,
)


def register_callbacks(app):
    # ── 1. Chargement des données depuis l'API ──────────────────────
    @app.callback(
        Output("heatmap-apc-raw-store", "data"),
        Input("token", "data"),
        prevent_initial_call=False,
    )
    def load_apc_data(token):
        if not token or token == "none":
            return None
        try:
            df_competences = get_apc_competences(token)
            df_niveaux = get_apc_niveaux(token)
            df_apprentissages = get_apc_apprentissages(token)
            df_ac_modules_raw = get_apc_ac_modules(token)
            df_modules = get_apc_modules(token)
            df_composantes = get_apc_composantes(token)

            # Construction de df_main (même logique que learnagement_dashboard_final.py)
            df_base = df_apprentissages.merge(df_niveaux, on="id_niveau", how="left").merge(
                df_competences, on="id_competence", how="left"
            )

            ac_agg = (
                df_ac_modules_raw.groupby("id_apprentissage_critique")
                .agg({"id_module": list, "type_lien": list})
                .reset_index()
            )
            ac_agg.columns = ["id_apprentissage_critique", "modules_list", "types_lien_list"]

            df_main = df_base.merge(ac_agg, on="id_apprentissage_critique", how="left")
            df_main["modules_list"] = df_main["modules_list"].apply(
                lambda x: x if isinstance(x, list) else []
            )
            df_main["types_lien_list"] = df_main["types_lien_list"].apply(
                lambda x: x if isinstance(x, list) else []
            )
            df_main["nb_modules"] = df_main["modules_list"].apply(len)
            df_main["id_module"] = df_main["modules_list"].apply(lambda x: x[0] if x else 0)
            df_main["type_lien"] = df_main["types_lien_list"].apply(
                lambda x: x[0] if x else "Non associé"
            )
            df_main["competence_label"] = df_main["code_competence"]
            df_main["niveau_code"] = (
                df_main["competence_label"] + "-N" + df_main["niveau"].astype(str)
            )

            mask = df_main["id_module"].isna()
            if mask.sum() > 0:
                df_main.loc[mask, "id_module"] = 0.0
                df_main.loc[mask, "type_lien"] = "Non associé"

            # Dictionnaire module_names (clés en string pour JSON)
            module_names = {"0": "Non associé", "0.0": "Non associé"}
            for _, row in df_modules.iterrows():
                mid = row["id_module"]
                code = row["code_module"] if pd.notna(row["code_module"]) else f"M{mid}"
                nom = row["nom"] if pd.notna(row["nom"]) else "Module"
                module_names[str(mid)] = f"{code} - {nom}"

            # Reverse : nom → id_module (string)
            module_ids = {v: k for k, v in module_names.items()}

            return {
                "df_main": df_main.to_json(date_format="iso", orient="split"),
                "df_composantes": df_composantes.to_json(date_format="iso", orient="split"),
                "module_names": module_names,
                "module_ids": module_ids,
            }

        except Exception as e:
            logging.exception(f"[heatmap_apc] Erreur chargement données APC : {e}")
            return None

    # ── 2. Filtrage ────────────────────────────────────────────────
    @app.callback(
        Output("heatmap-apc-filtered-store", "data"),
        Output("heatmap-apc-filter-status", "children"),
        Input("heatmap-apc-niveau-filter", "value"),
        Input("heatmap-apc-comp-filter", "value"),
        Input("heatmap-apc-lien-filter", "value"),
        Input("heatmap-apc-reset-filters", "n_clicks"),
        Input("heatmap-apc-raw-store", "data"),
        prevent_initial_call=False,
    )
    def filter_data(niveaux, competences, types_lien, reset_clicks, raw_data):
        if raw_data is None:
            return None, "Chargement..."

        df = pd.read_json(StringIO(raw_data["df_main"]), orient="split")
        ctx = dash.callback_context
        trigger = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else ""

        if trigger == "heatmap-apc-reset-filters":
            return raw_data["df_main"], f"{len(df)} objectifs affichés"

        filtered = df.copy()
        if niveaux:
            filtered = filtered[filtered["niveau"].isin(niveaux)]
        if competences:
            filtered = filtered[filtered["competence_label"].isin(competences)]
        if types_lien:
            filtered = filtered[filtered["type_lien"].isin(types_lien)]

        return filtered.to_json(
            date_format="iso", orient="split"
        ), f"{len(filtered)} / {len(df)} objectifs"

    # ── 3. Drill-down heatmap ──────────────────────────────────────
    @app.callback(
        Output("heatmap-apc-drilldown", "figure"),
        Output("heatmap-apc-drill-level", "data"),
        Output("heatmap-apc-selected-niveau", "data"),
        Output("heatmap-apc-selected-module", "data"),
        Output("heatmap-apc-breadcrumb", "children"),
        Input("heatmap-apc-filtered-store", "data"),
        Input("heatmap-apc-drilldown", "clickData"),
        Input("heatmap-apc-btn-global", "n_clicks"),
        Input("heatmap-apc-btn-back", "n_clicks"),
        State("heatmap-apc-drill-level", "data"),
        State("heatmap-apc-selected-niveau", "data"),
        State("heatmap-apc-selected-module", "data"),
        State("heatmap-apc-raw-store", "data"),
        prevent_initial_call=False,
    )
    def update_heatmap_drilldown(
        filtered_json,
        clickData,
        _btn_global,
        _btn_back,
        current_level,
        current_niveau,
        current_module,
        raw_data,
    ):
        if filtered_json is None or raw_data is None:
            return (
                _empty_fig("En attente des données…"),
                "global",
                None,
                None,
                html.Span("Vue globale"),
            )

        # Reconstruction de module_names avec clés numériques
        module_names_str = raw_data.get("module_names", {})
        module_ids_str = raw_data.get("module_ids", {})
        module_names = {}
        for k, v in module_names_str.items():
            try:
                module_names[float(k)] = v
            except ValueError, TypeError:
                module_names[k] = v

        filtered_df = pd.read_json(StringIO(filtered_json), orient="split")
        filtered_df["niveau_code"] = filtered_df.apply(parse_competencies, axis=1)
        filtered_df = filtered_df.assign(All_Competencies=filtered_df["niveau_code"])

        ctx = dash.callback_context
        trigger = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else "none"

        new_level = current_level or "global"
        new_niveau = current_niveau
        new_module = current_module

        if trigger == "heatmap-apc-btn-global":
            new_level, new_niveau, new_module = "global", None, None

        elif trigger == "heatmap-apc-btn-back":
            if current_level == "module":
                new_level, new_module = "semester", None
            elif current_level == "semester":
                new_level, new_niveau = "global", None

        elif trigger == "heatmap-apc-drilldown" and clickData and "points" in clickData:
            point = clickData["points"][0]
            if current_level in [None, "global"]:
                clicked = point.get("y")
                if clicked is not None:
                    try:
                        new_niveau = int(clicked)
                        new_level = "semester"
                        new_module = None
                    except ValueError, TypeError:
                        pass
            elif current_level == "semester":
                # Utilise customdata (ID du module) si disponible, sinon fallback sur le nom
                customdata_val = point.get("customdata")
                if customdata_val is not None:
                    try:
                        raw = (
                            customdata_val[0]
                            if isinstance(customdata_val, list)
                            else customdata_val
                        )
                        new_module = float(raw)
                        new_level = "module"
                    except ValueError, TypeError:
                        pass
                else:
                    clicked_name = point.get("y")
                    if clicked_name is not None:
                        clicked_id = module_ids_str.get(clicked_name)
                        if clicked_id is not None:
                            try:
                                new_module = float(clicked_id)
                                new_level = "module"
                            except ValueError, TypeError:
                                pass

        try:
            df_pivot_global, df_pivot_niveau, df_pivot_module = (
                compute_competency_counts_per_module(filtered_df)
            )
        except Exception as e:
            return _empty_fig(f"Erreur : {e}"), "global", None, None, html.Span("Erreur")

        # ── Rendu selon le niveau de drill-down ──
        if new_level == "global":
            fig = create_heatmap_for_global(df_pivot_global)
            breadcrumb = html.Span("Vue globale", style={"fontWeight": "600"})

        elif new_level == "semester" and new_niveau is not None:
            available = df_pivot_niveau.index.get_level_values("niveau").unique().tolist()
            if new_niveau in available:
                fig = create_heatmap_for_niveau(new_niveau, df_pivot_niveau, module_names)
                breadcrumb = html.Span(
                    [
                        html.Span("Vue globale", style={"color": "#6B7280"}),
                        html.Span(" / "),
                        html.Span(f"Niveau {new_niveau}", style={"fontWeight": "600"}),
                    ]
                )
            else:
                fig = create_heatmap_for_global(df_pivot_global)
                new_level, new_niveau = "global", None
                breadcrumb = html.Span("Vue globale", style={"fontWeight": "600"})

        elif new_level == "module" and new_module is not None:
            available = df_pivot_module.index.get_level_values("id_module").unique().tolist()
            if new_module in available:
                fig = create_heatmap_for_module(new_module, df_pivot_module, module_names)
                module_name = module_names.get(new_module, f"Module {new_module}")
                breadcrumb = html.Span(
                    [
                        html.Span("Vue globale", style={"color": "#6B7280"}),
                        html.Span(" / "),
                        html.Span(f"Niveau {new_niveau}", style={"color": "#6B7280"}),
                        html.Span(" / "),
                        html.Span(module_name, style={"fontWeight": "600"}),
                    ]
                )
            else:
                fig = create_heatmap_for_global(df_pivot_global)
                new_level, new_niveau, new_module = "global", None, None
                breadcrumb = html.Span("Vue globale", style={"fontWeight": "600"})

        else:
            fig = create_heatmap_for_global(df_pivot_global)
            new_level, new_niveau, new_module = "global", None, None
            breadcrumb = html.Span("Vue globale", style={"fontWeight": "600"})

        return fig, new_level, new_niveau, new_module, breadcrumb
