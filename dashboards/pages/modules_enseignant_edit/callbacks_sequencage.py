from pages import modules_tools
import app_tools
import pandas as pd
from dash import Input, Output, State, dash_table
from pandas.core.interchange.dataframe_protocol import DataFrame

from .queries import update_table_sequencage, update_table_sequence


def register_sequencage_callbacks(app):
    # Mise à jour du filtre des modules en fonction de l'utilisateur
    @app.callback(
        Output("filtre_module", "options"),
        Input("user_id", "data"),
        State("token", "data"),
    )
    def update_filter_sequencage_option(user_id, token):
        df = modules_tools.get_moduleByEnseignantId(token, user_id)
        options = []
        if not df.empty:
            options = [
                {"label": row["code_module"], "value": row["id_module"]}
                for _, row in df[["id_module", "code_module"]].drop_duplicates().iterrows()
            ]
        return options

    @app.callback(
        Output("app5_ens_edit_title", "children"),
        Input("filtre_module", "value"),
        State("user_id", "data"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def update_title(id_module: int, user_id: int, token):
        nom_module = ""
        df = modules_tools.get_moduleByEnseignantId(token, user_id)
        if not df.empty and id_module:
            nom_module = (
                df[df["id_module"] == id_module][["nom_module"]]
                .drop_duplicates()
                .iloc[0]["nom_module"]
            )
        return "Séquençage: " + nom_module

    # Création de la ligne d'ajout de séquençage
    @app.callback(
        Output("add_sequencage_div", "children"),
        State("user_id", "data"),
        Input("filtre_module", "value"),
        State("token", "data"),
    )
    def add_table_sequencage(user_id, selected_module, token):
        if not selected_module:
            return []
        df = modules_tools.get_moduleSequencageByEnseignantId(token, user_id)
        if df.empty:
            df = pd.DataFrame(
                columns=["nombre", "type", "duree_h", "groupe_type", "intervenant_principal"]
            )
        df = df[["nombre", "type", "duree_h", "groupe_type", "intervenant_principal"]]
        columns = [
            {"name": i, "id": i, "editable": True, "presentation": "dropdown"}
            if i in ["intervenant_principal", "type", "groupe_type"]
            else {"name": i, "id": i, "editable": True}
            for i in df.columns
        ]
        data = {i: "" for i in df.columns}
        df = app_tools.get_groupe_types(token)
        groupe_type_options = [
            {"label": row["ExplicitSecondaryK"], "value": row["id_groupe_type"]}
            for _, row in df.iterrows()
        ]
        df = app_tools.get_enseignants(token)
        intervenant_options = [
            {"label": row["ExplicitSecondaryK"], "value": row["id_enseignant"]}
            for _, row in df.iterrows()
        ]
        df = app_tools.get_seance_types(token)
        seance_type_options = [
            {"label": row["ExplicitSecondaryK"], "value": row["id_seance_type"]}
            for _, row in df.iterrows()
        ]

        table_intervenants = dash_table.DataTable(
            id="add_table",
            columns=columns,
            data=[data],
            dropdown={
                "type": {"options": seance_type_options},
                "intervenant_principal": {"options": intervenant_options},
                "groupe_type": {"options": groupe_type_options},
            },
        )

        return [table_intervenants]

    # Ajout d'un séquençage au clic sur le bouton
    @app.callback(
        Output("sequencage_div", "children", allow_duplicate=True),
        State("user_id", "data"),
        State("filtre_module", "value"),
        State("add_table", "data"),
        Input("add_sequencage_button", "n_clicks"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_add_sequencage(user_id: int, selected_module, data, button_n_clicks, token):
        if not selected_module:
            return []
        data[0]["id_module"] = selected_module
        data[0]["id_seance_type"] = data[0]["type"]
        data[0]["id_groupe_type"] = data[0]["groupe_type"]
        data[0]["id_intervenant_principal"] = data[0]["intervenant_principal"]
        modules_tools.add_moduleSequencage(token, data[0])
        return update_table_sequencage(token, user_id, selected_module)

    # Remove
    @app.callback(
        Input("table_sequencage", "data_previous"),
        State("table_sequencage", "data"),
        State("user_id", "data"),
        State("filtre_module", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_remove_sequencag(previous, current, user_id, id_module, token):
        if previous is None:
            print("Kaboum", flush=True)
        elif len(previous) > len(current):  # else row updated
            to_remove = [row for row in previous if row not in current][0]
            df = modules_tools.get_moduleSequencageByEnseignantId(token, user_id)
            id_to_remove = df[
                (df["nombre"] == to_remove["nombre"])
                & (df["type"] == to_remove["type"])
                & (df["duree_h"] == to_remove["duree_h"])
                & (df["groupe_type"] == to_remove["groupe_type"])
            ][["id_module_sequencage"]].iat[0, 0]
            modules_tools.remove_moduleSequencage(token, id_module, id_to_remove)

    # Changement d'intervenant principal au niveau séquençage
    @app.callback(
        Output("sequencage_div", "children", allow_duplicate=True),
        Output("sequence_div", "children"),
        Input("table_sequencage", "data_previous"),
        State("table_sequencage", "data"),
        State("user_id", "data"),
        State("filtre_module", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_change_intervenant_sequencage(previous, current, user_id: int, id_module: int, token):
        if previous is None:
            return update_table_sequencage(token, user_id, id_module), update_table_sequence(
                token, user_id, id_module, None
            )
        else:
            row_changed = [row for row in current if row not in previous]
            if len(row_changed) > 0:  # else callback invoked by data deleted
                df = modules_tools.get_moduleSequencageByEnseignantId(token, user_id)
                print(df, flush=True)
                row_changed = row_changed[0]
                new_intervenant_id = row_changed["nouvel_intervenant"]
                if new_intervenant_id is None or new_intervenant_id == "":
                    new_intervenant_id = None
                id_sequencage = int(
                    df[
                        (df["id_module"] == id_module)
                        & (df["nombre"] == row_changed["nombre"])
                        & (df["type"] == row_changed["type"])
                        & (df["duree_h"] == row_changed["duree_h"])
                        & (df["groupe_type"] == row_changed["groupe_type"])
                    ][["id_module_sequencage"]].iat[0, 0]
                )
                if new_intervenant_id is None or new_intervenant_id == "":
                    modules_tools.reset_intervenant_principal_sequencage(
                        token, id_module, id_sequencage
                    )
                else:
                    modules_tools.set_intervenant_principal_sequencage(
                        token, id_module, id_sequencage, new_intervenant_id
                    )
            return update_table_sequencage(token, user_id, id_module), update_table_sequence(
                token, user_id, id_module, None
            )

    # Mise à jour de la table des séquençages selon le module sélectionné
    @app.callback(
        Output("sequencage_div", "children"),
        State("user_id", "data"),
        Input("filtre_module", "value"),
        State("token", "data"),
    )
    def cb_update_table_sequencage(user_id, selected_module, token):
        return update_table_sequencage(token, user_id, selected_module)

    @app.callback(
        Output("sequencage_vs_maquette_div", "children"),
        Input("table_sequencage", "data"),
        State("filtre_module", "value"),
        State("user_id", "data"),
        State("token", "data"),
    )
    def cb_check_sequencage_vs_maquette(data, id_module, user_id, token):
        df = modules_tools.check_moduleSequencage(token, user_id)

        if df.empty:
            df = DataFrame(
                columns=[
                    "id_module",
                    "code_module",
                    "CM_to_plan",
                    "TD_to_plan",
                    "TP_to_plan",
                    "Proj_to_plan",
                ]
            )
        if id_module:
            df = df[df["id_module"] == id_module][
                ["code_module", "CM_to_plan", "TD_to_plan", "TP_to_plan", "Proj_to_plan"]
            ]

        table_check = dash_table.DataTable(
            id="check_table",
            data=df.to_dict("records"),
        )

        return [table_check]
