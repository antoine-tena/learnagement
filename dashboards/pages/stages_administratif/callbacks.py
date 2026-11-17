from time import sleep

from pages import stages_tools
import app_tools
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .queries import (
    get_entreprises,
    get_students_without_internship,
    get_teachers,
    update_pie_chart,
    update_table_stages_with_supervisor,
    update_table_stages_without_supervisor,
    update_table_students_without_internship,
)


def register_callbacks(app):
    # Mise à jour du filtre des promo en fonction du module selectionné
    @app.callback(
        Output("app10_filtre_promo", "options"),
        Output("etudiant_input", "options"),
        Output("entreprise_input", "options"),
        Output("tuteur_input", "options"),
        Input("user_id", "data"),
        State("token", "data"),
    )
    def update_options(user_id, token):
        df = app_tools.get_promos(token)
        promo_options = [
            {"label": row["promo"], "value": row["promo"]} for _, row in df[["promo"]].iterrows()
        ]
        etudiant_options = [
            {"label": k, "value": v} for k, v in get_students_without_internship(token).items()
        ]
        entreprise_options = [{"label": v, "value": v} for v in get_entreprises(token)]
        return promo_options, etudiant_options, entreprise_options, get_teachers(token)

    @app.callback(
        Output(component_id="div_stages_with_supervisor", component_property="children"),
        Output(component_id="div_stages_without_supervisor", component_property="children"),
        Output(component_id="div_students_without_stage", component_property="children"),
        Input("user_id", "data"),
        Input("app10_filtre_promo", "value"),
        State("token", "data"),
    )
    def init_tables(user_id, nom_promo, token):
        return (
            update_table_stages_with_supervisor(nom_promo, token),
            update_table_stages_without_supervisor(nom_promo, token),
            update_table_students_without_internship(nom_promo, token),
        )

    # Store entreprise into dash list (not in db)
    @app.callback(
        Output("new_entreprise_input", "value"),
        Output("entreprise_input", "placeholder"),
        Input("entreprise_input", "search_value"),
        State("new_entreprise_input", "value"),
        prevent_initial_call=True,
    )
    def store_new_entreprise(search_value, new_entreprise_input):
        value = search_value
        if search_value == "":
            value = new_entreprise_input
        return value, value

    @app.callback(
        Output(component_id="submit-button", component_property="children", allow_duplicate=True),
        Output(component_id="div_pie_chart", component_property="children", allow_duplicate=True),
        Output(
            component_id="div_stages_with_supervisor",
            component_property="children",
            allow_duplicate=True,
        ),
        Output(
            component_id="div_stages_without_supervisor",
            component_property="children",
            allow_duplicate=True,
        ),
        Output(
            component_id="div_students_without_stage",
            component_property="children",
            allow_duplicate=True,
        ),
        Input(component_id="submit-button", component_property="n_clicks"),
        State("app10_filtre_promo", "value"),
        State("entreprise_input", "value"),
        State("new_entreprise_input", "value"),
        State("sujet_input", "value"),
        State("mission_input", "value"),
        State("ville_input", "value"),
        State("dates_input", "start_date"),
        State("dates_input", "end_date"),
        State("etudiant_input", "value"),
        State("tuteur_input", "value"),
        State("token", "data"),
        prevent_initial_call=True,
        running=[(Output("submit-button", "disabled"), True, False)],
    )
    def save_stage(
        save_button,
        nom_promo,
        entreprise,
        new_entreprise,
        sujet,
        mission,
        ville,
        start_date,
        end_date,
        id_etudiant,
        id_enseignant,
        token,
    ):
        if (
            id_etudiant
            and (entreprise or new_entreprise)
            and sujet
            and mission
            and start_date
            and end_date
        ):
            if not entreprise:
                entreprise = new_entreprise
            save_status = stages_tools.add_stage(
                token,
                entreprise,
                sujet,
                mission,
                ville,
                start_date,
                end_date,
                id_etudiant,
                id_enseignant,
            )
            print(save_status, flush=True)
            return (
                save_status,
                [update_pie_chart(token, nom_promo)],
                update_table_stages_with_supervisor(nom_promo, token),
                update_table_stages_without_supervisor(nom_promo, token),
                update_table_students_without_internship(nom_promo, token),
            )
        else:
            raise PreventUpdate

    @app.callback(
        Output(component_id="submit-button", component_property="children"),
        Input(component_id="submit-button", component_property="children"),
        prevent_initial_call=True,
    )
    def button_text(text):
        sleep(1)
        return "Save the data"

    # set internship advisor
    @app.callback(
        Output(component_id="div_pie_chart", component_property="children", allow_duplicate=True),
        Output(
            component_id="div_stages_with_supervisor",
            component_property="children",
            allow_duplicate=True,
        ),
        Output(
            component_id="div_stages_without_supervisor",
            component_property="children",
            allow_duplicate=True,
        ),
        Input("table_stages_without_supervisor", "data_previous"),
        State("table_stages_without_supervisor", "data"),
        State("app10_filtre_promo", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_set_internship_supervisor(previous, current, nom_promo, token):
        if previous is None or current is None:
            return (
                [update_pie_chart(token, nom_promo)],
                update_table_stages_with_supervisor(nom_promo, token),
                update_table_stages_without_supervisor(nom_promo, token),
            )
        elif len(previous) > len(current):  # else row updated
            to_remove = [row for row in previous if row not in current][0]
            id_etudiant = to_remove["id_etudiant"]
            id_to_remove = to_remove["id_stage"]
            stages_tools.remove_stage(token, id_etudiant, id_to_remove)
        else:
            row_changed = [row for row in current if row not in previous]
            if len(row_changed) > 0:  # else callback invoked by data deleted
                row_changed = row_changed[0]
                new_supervisor_id = row_changed["nouveau_tuteur"]
                id_stage = row_changed["id_stage"]
                id_etudiant = row_changed["id_etudiant"]
                stages_tools.set_internship_supervisor(
                    token, id_etudiant, id_stage, new_supervisor_id
                )
        return (
            [update_pie_chart(token, nom_promo)],
            update_table_stages_with_supervisor(nom_promo, token),
            update_table_stages_without_supervisor(nom_promo, token),
        )

    @app.callback(
        Output(
            component_id="div_stages_with_supervisor",
            component_property="children",
            allow_duplicate=True,
        ),
        Output(
            component_id="div_stages_without_supervisor",
            component_property="children",
            allow_duplicate=True,
        ),
        Input("table_stages_with_supervisor", "data_previous"),
        State("table_stages_with_supervisor", "data"),
        State("app10_filtre_promo", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_reset_internship_supervisor(previous, current, nom_promo, token):
        if previous is not None and current is not None and len(previous) == len(current):
            row_changed = [row for row in current if row not in previous]
            if len(row_changed) > 0:  # else callback invoked by data deleted
                row_changed = row_changed[0]
                new_supervisor_id = row_changed["nouveau_tuteur"]
                id_stage = row_changed["id_stage"]
                id_etudiant = row_changed["id_etudiant"]
                stages_tools.set_internship_supervisor(
                    token, id_etudiant, id_stage, new_supervisor_id
                )
        return update_table_stages_with_supervisor(
            nom_promo, token
        ), update_table_stages_without_supervisor(nom_promo, token)

    # Remove stage with supervisor
    @app.callback(
        Output(component_id="div_pie_chart", component_property="children", allow_duplicate=True),
        Input("table_stages_with_supervisor", "data_previous"),
        State("table_stages_with_supervisor", "data"),
        State("app10_filtre_promo", "value"),
        State("token", "data"),
        prevent_initial_call=True,
    )
    def cb_remove_stage_with(previous, current, nom_promo, token):
        if (
            previous is not None and current is not None and len(previous) > len(current)
        ):  # else row updated
            to_remove = [row for row in previous if row not in current][0]
            id_etudiant = to_remove["id_etudiant"]
            id_to_remove = to_remove["id_stage"]
            stages_tools.remove_stage(token, id_etudiant, id_to_remove)
        return [update_pie_chart(token, nom_promo)]
