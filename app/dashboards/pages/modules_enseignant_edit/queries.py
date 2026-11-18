from pages import modules_tools
import app_tools
import pandas as pd
from dash import dash_table


def update_table_sequencage(token, user_id, selected_module):
    if not selected_module:
        return []
    df = modules_tools.get_moduleSequencageByEnseignantId(token, user_id)
    if df.empty:
        df = pd.DataFrame(
            columns=[
                "id_module",
                "nombre",
                "type",
                "duree_h",
                "groupe_type",
                "intervenant_principal",
            ]
        )
    df = df[df["id_module"] == selected_module][
        ["nombre", "type", "duree_h", "groupe_type", "intervenant_principal"]
    ]
    dfi = app_tools.get_enseignants(token)
    intervenant_options = [{"label": "Aucun intervenant", "value": None}] + [
        {"label": row["ExplicitSecondaryK"], "value": row["id_enseignant"]}
        for _, row in dfi.iterrows()
    ]

    table_sequencage = dash_table.DataTable(
        id="table_sequencage",
        columns=[{"name": i, "id": i} for i in df.columns]
        + [
            {
                "name": "nouvel_intervenant",
                "id": "nouvel_intervenant",
                "editable": True,
                "presentation": "dropdown",
            }
        ],
        data=df.to_dict("records"),
        editable=True,
        row_deletable=True,
        dropdown={
            "nouvel_intervenant": {
                "options": intervenant_options,
                "clearable": True,
            }
        },
    )
    return [table_sequencage]


def update_table_sequence(token, user_id, selected_module, selected_seance_type):
    if not selected_module:
        return []
    df = modules_tools.get_moduleSequenceByEnseignantId(token, user_id)
    if not df.empty:
        if selected_seance_type:
            df = df[
                (df["id_module"] == selected_module)
                & (df["id_seance_type"] == selected_seance_type)
            ][
                [
                    "id_sequence",
                    "type",
                    "duree_h",
                    "groupe_type",
                    "numero_ordre",
                    "intervenant_principal",
                    "commentaire",
                ]
            ]
        else:  # display all sequence types
            df = df[df["id_module"] == selected_module][
                [
                    "id_sequence",
                    "type",
                    "numero_ordre",
                    "duree_h",
                    "groupe_type",
                    "intervenant_principal",
                    "commentaire",
                ]
            ]

        dfi = app_tools.get_enseignants(token)
        intervenant_options = [{"label": "Aucun intervenant", "value": None}] + [
            {"label": row["ExplicitSecondaryK"], "value": row["id_enseignant"]}
            for _, row in dfi.iterrows()
        ]

        table_sequence = dash_table.DataTable(
            id="table_sequence",
            columns=[{"name": i, "id": i} for i in df.columns]
            + [
                {
                    "name": "nouvel_intervenant",
                    "id": "nouvel_intervenant",
                    "editable": True,
                    "presentation": "dropdown",
                }
            ],
            editable=True,
            data=df.to_dict("records"),
            row_deletable=False,
            dropdown={
                "nouvel_intervenant": {
                    "options": intervenant_options,
                    "clearable": True,
                }
            },
            style_cell_conditional=[
                {
                    "if": {
                        "column_id": "id_sequence",
                    },
                    "display": "None",
                }
            ],
        )
    else:
        table_sequence = dash_table.DataTable()
    return [table_sequence]


def update_table_session(token, user_id, selected_module, selected_seance_type, selected_promotion):
    if not selected_module:
        return []
    df = modules_tools.get_moduleSessionByEnseignantId(token, user_id)

    if not df.empty:
        if selected_seance_type and selected_promotion:
            df = df[
                (df["id_module"] == selected_module)
                & (df["id_seance_type"] == selected_seance_type)
                & (df["id_promo"] == selected_promotion)
            ][
                [
                    "id_session",
                    "type",
                    "duree_h",
                    "nom_groupe",
                    "numero_ordre",
                    "intervenant",
                    "commentaire",
                ]
            ].sort_values(by=["type", "numero_ordre"], ascending=[False, False])
        elif selected_seance_type:
            df = df[
                (df["id_module"] == selected_module)
                & (df["id_seance_type"] == selected_seance_type)
            ][
                [
                    "id_session",
                    "type",
                    "numero_ordre",
                    "duree_h",
                    "nom_groupe",
                    "intervenant",
                    "commentaire",
                ]
            ].sort_values(by=["type", "numero_ordre"], ascending=[False, False])
        elif selected_promotion:
            df = df[(df["id_module"] == selected_module) & (df["id_promo"] == selected_promotion)][
                [
                    "id_session",
                    "type",
                    "duree_h",
                    "nom_groupe",
                    "numero_ordre",
                    "intervenant",
                    "commentaire",
                ]
            ].sort_values(by=["type", "numero_ordre"], ascending=[False, False])
        else:
            df = df[(df["id_module"] == selected_module)][
                [
                    "id_session",
                    "type",
                    "numero_ordre",
                    "duree_h",
                    "nom_groupe",
                    "intervenant",
                    "commentaire",
                ]
            ].sort_values(by=["type", "numero_ordre"], ascending=[False, False])

        dfi = app_tools.get_enseignants(token)
        intervenant_options = [{"label": "Aucun intervenant", "value": None}] + [
            {"label": row["ExplicitSecondaryK"], "value": row["id_enseignant"]}
            for _, row in dfi.iterrows()
        ]

        table_session = dash_table.DataTable(
            id="table_session",
            columns=[{"name": i, "id": i} for i in df.columns]
            + [
                {
                    "name": "nouvel_intervenant",
                    "id": "nouvel_intervenant",
                    "editable": True,
                    "presentation": "dropdown",
                }
            ],
            data=df.to_dict("records"),
            sort_action="native",
            sort_mode="multi",
            row_deletable=False,
            dropdown={
                "nouvel_intervenant": {
                    "options": intervenant_options,
                    "clearable": True,
                }
            },
            style_cell_conditional=[
                {
                    "if": {
                        "column_id": "id_session",
                    },
                    "display": "None",
                }
            ],
        )
    else:
        table_session = dash_table.DataTable()
    return [table_session]
