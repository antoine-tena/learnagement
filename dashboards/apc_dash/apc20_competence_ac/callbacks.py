"""Callbacks Dash pour les graphiques et listes Compétences / AC et CE."""

from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from .queries import build_detail_list, load_competence_graph_data


def register_callbacks(app):
    # =========================================================
    # CALLBACKS AC
    # =========================================================
    @app.callback(
        Output("competence-data-store", "data"),
        Output("competence-graph", "figure"),
        Output("competence-dropdown", "options"),
        Output("competence-dropdown", "value"),
        Input("user_id", "data"),
        State("token", "data"),
    )
    def load_graph_ac(user_id, token):
        if not token:
            raise PreventUpdate
        return load_competence_graph_data(
            token=token,
            endpoint_path="/competence_ac/",
            id_col="id_apprentissage_critique",
            label_col="libelle_apprentissage",
            count_col="nb_ac",
            graph_title="Compétences - Nombre d’Apprentissages critiques (AC) associés",
        )

    @app.callback(
        Output("competence-dropdown", "value", allow_duplicate=True),
        Input("competence-graph", "clickData"),
        State("competence-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_dropdown_from_graph_ac(clickData, current_value):
        if not clickData or "points" not in clickData or len(clickData["points"]) == 0:
            raise PreventUpdate

        selected_competence = clickData["points"][0]["y"]
        if selected_competence == current_value:
            raise PreventUpdate

        return selected_competence

    @app.callback(
        Output("competence_ac", "children"),
        Input("competence-dropdown", "value"),
        State("competence-data-store", "data"),
    )
    def update_ac_list(selected_competence, stored_data):
        return build_detail_list(
            selected_competence=selected_competence,
            stored_data=stored_data,
            id_col="id_apprentissage_critique",
            label_col="libelle_apprentissage",
            section_label="Apprentissages critiques",
            empty_message="Aucun apprentissage critique trouvé.",
        )

    # =========================================================
    # CALLBACKS CE
    # =========================================================
    @app.callback(
        Output("competence-ce-data-store", "data"),
        Output("competence-ce-graph", "figure"),
        Output("competence-ce-dropdown", "options"),
        Output("competence-ce-dropdown", "value"),
        Input("user_id", "data"),
        State("token", "data"),
    )
    def load_graph_ce(user_id, token):
        if not token:
            raise PreventUpdate
        return load_competence_graph_data(
            token=token,
            endpoint_path="/competence_ce/",
            id_col="id_composante_essentielle",
            label_col="libelle_composante_essentielle",
            count_col="nb_ce",
            graph_title="Compétences - Nombre de Composantes essentielles (CE) associées",
        )

    @app.callback(
        Output("competence-ce-dropdown", "value", allow_duplicate=True),
        Input("competence-ce-graph", "clickData"),
        State("competence-ce-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_dropdown_from_graph_ce(clickData, current_value):
        if not clickData or "points" not in clickData or len(clickData["points"]) == 0:
            raise PreventUpdate

        selected_competence = clickData["points"][0]["y"]
        if selected_competence == current_value:
            raise PreventUpdate

        return selected_competence

    @app.callback(
        Output("competence_ce", "children"),
        Input("competence-ce-dropdown", "value"),
        State("competence-ce-data-store", "data"),
    )
    def update_ce_list(selected_competence, stored_data):
        return build_detail_list(
            selected_competence=selected_competence,
            stored_data=stored_data,
            id_col="id_composante_essentielle",
            label_col="libelle_composante_essentielle",
            section_label="Composantes essentielles",
            empty_message="Aucune composante essentielle trouvée.",
        )
