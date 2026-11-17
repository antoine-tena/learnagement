from pages import modules_tools
from dash import Input, Output, State

from .callbacks_sequencage import register_sequencage_callbacks
from .queries import update_table_sequencage, update_table_sequence, update_table_session


def register_callbacks_edit(app):
    register_sequencage_callbacks(app)

    # Mise à jour du filtre des types de cours en fonction du module selectionné
    @app.callback(
        Output("filtre_type", "options"),
        State("user_id", "data"),
        Input("filtre_module", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def update_filter_sequence_option(user_id, selected_module, token):
        df = modules_tools.get_moduleSequenceByEnseignantId(token, user_id)
        options = []
        if not df.empty:
            options = [
                {"label": row["type"], "value": row["id_seance_type"]}
                for _, row in df[df["id_module"] == selected_module][["id_seance_type", "type"]]
                .drop_duplicates()
                .iterrows()
            ]
        return options

    # Mise à jour de la table des séances (séquences) selon le module sélectionné et le type de cours
    @app.callback(
        Output("sequence_div", "children", allow_duplicate=True),
        State("user_id", "data"),
        Input("filtre_module", "value"),
        Input("filtre_type", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_update_table_sequence(user_id, selected_module, selected_type, token):
        return update_table_sequence(token, user_id, selected_module, selected_type)

    @app.callback(
        Output("sequence_div", "children", allow_duplicate=True),
        Output("session_div", "children"),
        Input("table_sequence", "data_previous"),
        State("table_sequence", "data"),
        State("user_id", "data"),
        State("filtre_module", "value"),
        Input("filtre_type", "value"),
        Input("filtre_promo", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_change_intervenant_sequence(
        previous, current, user_id, selected_module, selected_type, selected_promo, token
    ):
        if previous is None:
            return (
                update_table_sequence(token, user_id, selected_module, selected_type),
                update_table_session(
                    token, user_id, selected_module, selected_type, selected_promo
                ),
            )
        else:
            row_changed = [row for row in current if row not in previous]
            if len(row_changed) > 0:  # else callback invoked by data deleted
                row_changed = row_changed[0]
                new_intervenant_id = int(row_changed["nouvel_intervenant"])
                id_sequence = int(row_changed["id_sequence"])
                if new_intervenant_id is None or new_intervenant_id == "":
                    modules_tools.reset_intervenant_principal_sequence(
                        token, selected_module, id_sequence
                    )
                else:
                    modules_tools.set_intervenant_principal_sequence(
                        token, selected_module, id_sequence, new_intervenant_id
                    )
                return (
                    update_table_sequencage(token, user_id, selected_module),
                    update_table_session(
                        token, user_id, selected_module, selected_type, selected_promo
                    ),
                )

    # Mise à jour du filtre des promo en fonction du module selectionné
    @app.callback(
        Output("filtre_promo", "options"),
        State("user_id", "data"),
        Input("filtre_module", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def update_filter_session_option(user_id, selected_module, token):
        df = modules_tools.get_moduleSessionByEnseignantId(token, user_id)

        options = []
        if not df.empty:
            options = [
                {"label": row["promo"], "value": row["id_promo"]}
                for _, row in df[df["id_module"] == selected_module][["id_promo", "promo"]]
                .drop_duplicates()
                .iterrows()
            ]
        return options

    # Update session table
    @app.callback(
        Output("session_div", "children", allow_duplicate=True),
        State("user_id", "data"),
        Input("filtre_module", "value"),
        Input("filtre_type", "value"),
        Input("filtre_promo", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_update_table_session(user_id, selected_module, selected_type, selected_promo, token):
        return update_table_session(token, user_id, selected_module, selected_type, selected_promo)

    # Update teacher session
    @app.callback(
        Output("session_div", "children", allow_duplicate=True),
        Input("table_session", "data_previous"),
        State("table_session", "data"),
        State("user_id", "data"),
        State("filtre_module", "value"),
        Input("filtre_type", "value"),
        Input("filtre_promo", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_change_intervenant_session(
        previous, current, user_id, selected_module, selected_type, selected_promo, token
    ):
        if previous is None:
            return update_table_session(
                token, user_id, selected_module, selected_type, selected_promo
            )
        else:
            row_changed = [row for row in current if row not in previous]
            if len(row_changed) > 0:  # else callback invoked by data deleted
                row_changed = row_changed[0]
                new_intervenant_id = int(row_changed["nouvel_intervenant"])
                id_session = int(row_changed["id_session"])
                if new_intervenant_id is None or new_intervenant_id == "":
                    modules_tools.reset_intervenant_session(token, selected_module, id_session)
                else:
                    modules_tools.set_intervenant_session(
                        token, selected_module, id_session, new_intervenant_id
                    )
                return update_table_session(
                    token, user_id, selected_module, selected_type, selected_promo
                )
