import app10_stage_tools
import app_tools
import plotly.graph_objects as go
from dash import dash_table, dcc


def get_entreprises(token):
    df_stages_with_supervisor = app10_stage_tools.get_stages_with_supervisorId(token)
    df_stages_without_supervisor = app10_stage_tools.get_stages_without_supervisorId(token)

    # liste des entreprises
    entreprises = []
    if "entreprise" in df_stages_with_supervisor.columns.tolist():
        entreprises = entreprises + df_stages_with_supervisor["entreprise"].tolist()
    if "entreprise" in df_stages_without_supervisor.columns.tolist():
        entreprises = entreprises + df_stages_without_supervisor["entreprise"].tolist()
    entreprises.sort()
    return entreprises


def get_teachers(token):
    dfi = app_tools.get_enseignants(token)
    intervenant_options = [
        {"label": row["ExplicitSecondaryK"], "value": row["id_enseignant"]}
        for _, row in dfi.iterrows()
    ]
    return intervenant_options


def get_internship_with_supervisor(token):
    df_stages_with_supervisor = app10_stage_tools.get_stages_with_supervisorId(token)
    return df_stages_with_supervisor


def update_table_stages_with_supervisor(nom_promo, token):
    df = app10_stage_tools.get_stages_with_supervisorId(token)

    if nom_promo and not df.empty:
        df = df[df["promo"] == nom_promo]

    dfi = app_tools.get_enseignants(token)
    intervenant_options = [
        {"label": row["ExplicitSecondaryK"], "value": row["id_enseignant"]}
        for _, row in dfi.iterrows()
    ]

    table_stages_with_supervisor = dash_table.DataTable(
        id="table_stages_with_supervisor",
        columns=[{"name": i, "id": i} for i in df.columns]
        + [
            {
                "name": "nouveau_tuteur",
                "id": "nouveau_tuteur",
                "editable": True,
                "presentation": "dropdown",
            }
        ],
        editable=True,
        sort_action="native",
        sort_mode="multi",
        data=df.to_dict("records"),
        row_deletable=True,
        dropdown={
            "nouveau_tuteur": {
                "options": intervenant_options,
                "clearable": True,
            }
        },
        style_cell_conditional=[
            {
                "if": {
                    "column_id": "id_stage",
                },
                "display": "None",
            },
            {
                "if": {
                    "column_id": "id_etudiant",
                },
                "display": "None",
            },
        ],
    )
    return table_stages_with_supervisor


def get_internship_without_supervisor(token):
    df_stages_without_supervisor = app10_stage_tools.get_stages_without_supervisorId(token)
    return df_stages_without_supervisor


def update_table_stages_without_supervisor(nom_promo, token):
    df = app10_stage_tools.get_stages_without_supervisorId(token)

    if nom_promo and not df.empty:
        df = df[df["promo"] == nom_promo]

    dfi = app_tools.get_enseignants(token)
    intervenant_options = [
        {"label": row["ExplicitSecondaryK"], "value": row["id_enseignant"]}
        for _, row in dfi.iterrows()
    ]

    table_stages_without_supervisor = dash_table.DataTable(
        id="table_stages_without_supervisor",
        columns=[{"name": i, "id": i} for i in df.columns]
        + [
            {
                "name": "nouveau_tuteur",
                "id": "nouveau_tuteur",
                "editable": True,
                "presentation": "dropdown",
            }
        ],
        editable=True,
        sort_action="native",
        sort_mode="multi",
        data=df.to_dict("records"),
        row_deletable=True,
        dropdown={
            "nouveau_tuteur": {
                "options": intervenant_options,
                "clearable": True,
            }
        },
        style_cell_conditional=[
            {
                "if": {
                    "column_id": "id_stage",
                },
                "display": "None",
            },
            {
                "if": {
                    "column_id": "id_etudiant",
                },
                "display": "None",
            },
        ],
    )
    return table_stages_without_supervisor


def get_students_without_internship(token):
    df_students_without_stage = app10_stage_tools.get_students_without_stage(token)
    df_students_without_stage.sort_values(by=["nom"], ascending=True, inplace=True)
    # liste des étudiants sans stage
    etudiants_sans_stage = {}
    if "nom" in df_students_without_stage.columns.tolist():
        etudiants_sans_stage_label = (
            df_students_without_stage["nom"].map(str)
            + " "
            + df_students_without_stage["prenom"].map(str)
        )
        etudiants_sans_stage_label = etudiants_sans_stage_label.tolist()
        etudiants_sans_stage_value = df_students_without_stage["id_etudiant"].tolist()
        etudiants_sans_stage = dict(zip(etudiants_sans_stage_label, etudiants_sans_stage_value))
    return etudiants_sans_stage


def update_table_students_without_internship(nom_promo, token):
    df = app10_stage_tools.get_students_without_stage(token)

    if nom_promo and not df.empty:
        df = df[df["promo"] == nom_promo]

    table_students_without_stage = dash_table.DataTable(
        id="table_students_without_stage",
        columns=[{"name": i, "id": i} for i in df.columns],
        editable=False,
        sort_action="native",
        sort_mode="multi",
        data=df.to_dict("records"),
        row_deletable=False,
        style_cell_conditional=[
            {
                "if": {
                    "column_id": "id_etudiant",
                },
                "display": "None",
            }
        ],
    )
    return table_students_without_stage


def update_pie_chart(token, nom_promo=None):
    if token:
        df_stages_with_supervisor = get_internship_with_supervisor(token)
        df_stages_without_supervisor = get_internship_without_supervisor(token)
        df_students_without_stage = app10_stage_tools.get_students_without_stage(token)

        if nom_promo:
            if not df_stages_with_supervisor.empty:
                df_stages_with_supervisor = df_stages_with_supervisor[
                    df_stages_with_supervisor["promo"] == nom_promo
                ]
            if not df_stages_without_supervisor.empty:
                df_stages_without_supervisor = df_stages_without_supervisor[
                    df_stages_without_supervisor["promo"] == nom_promo
                ]
            if not df_students_without_stage.empty:
                df_students_without_stage = df_students_without_stage[
                    df_students_without_stage["promo"] == nom_promo
                ]

        avec_stage_avec_tuteur = len(df_stages_with_supervisor)
        avec_stage_sans_tuteur = len(df_stages_without_supervisor)
        sans_stage = len(df_students_without_stage)

        fig_values = [avec_stage_avec_tuteur, avec_stage_sans_tuteur, sans_stage]
    else:
        fig_values = [0, 0, 1]
    fig_labels = ["Avec Stage et tuteur", "Avec Stage, sans tuteur", "Sans Stage"]

    # Création du pie chart
    fig = go.Figure(data=[go.Pie(labels=fig_labels, values=fig_values, hole=0.3)])

    # Personnalisation du pie chart
    fig.update_traces(marker=dict(colors=["#00FF00", "#0000FF", "#FF0000"]))
    fig.update_layout(title_text="Répartition des étudiants avec ou sans stage")

    return dcc.Graph(id="pie_chart", figure=fig)
