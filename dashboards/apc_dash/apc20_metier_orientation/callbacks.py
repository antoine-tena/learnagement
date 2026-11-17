"""Callbacks Dash de la vue Orientation par métier."""

from app_tools import get_endpoint, get_python_backend_url
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from .layout import COLOR_MAP, default_ac_panel, empty_figure


def register_callbacks(app):
    @app.callback(
        Output("metier-dropdown", "options"),
        Output("metier-dropdown", "value"),
        Input("user_id", "data"),
        Input("token", "data"),
    )
    def load_metiers(user_id, token):
        if not token:
            raise PreventUpdate

        url = get_python_backend_url("/metier/")
        data = get_endpoint(url, token=token)

        if data is None or len(data) == 0:
            return [], None

        df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
        if df.empty:
            return [], None

        required_cols = ["id_situation_professionnelle", "libelle_situation"]
        for col in required_cols:
            if col not in df.columns:
                return [], None

        df["libelle_situation"] = df["libelle_situation"].fillna("").astype(str).str.strip()
        df = df[df["libelle_situation"] != ""]
        if df.empty:
            return [], None

        df = (
            df[["id_situation_professionnelle", "libelle_situation"]]
            .drop_duplicates(subset=["id_situation_professionnelle"])
            .sort_values("libelle_situation")
        )
        options = [
            {"label": row["libelle_situation"], "value": row["id_situation_professionnelle"]}
            for _, row in df.iterrows()
        ]
        default_value = options[0]["value"] if options else None
        return options, default_value

    @app.callback(
        Output("metier-ac-store", "data"),
        Input("metier-dropdown", "value"),
        Input("token", "data"),
    )
    def load_metier_ac_data(selected_metier_id, token):
        if not token or selected_metier_id is None:
            raise PreventUpdate

        url = get_python_backend_url(f"/metier_ac/{selected_metier_id}")
        data = get_endpoint(url, token=token)

        if data is None or len(data) == 0:
            return []

        df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data.copy()
        if df.empty:
            return []

        required_cols = [
            "libelle_situation",
            "id_situation_professionnelle",
            "id_semestre",
            "semestre",
            "id_apprentissage_critique",
            "libelle_apprentissage",
            "id_competence",
            "code_competence",
        ]
        for col in required_cols:
            if col not in df.columns:
                return []

        df["libelle_situation"] = df["libelle_situation"].fillna("").astype(str).str.strip()
        df["semestre"] = df["semestre"].fillna("").astype(str).str.strip()
        df["libelle_apprentissage"] = df["libelle_apprentissage"].fillna("").astype(str).str.strip()
        df["code_competence"] = df["code_competence"].fillna("").astype(str).str.strip()

        df = df.dropna(subset=["id_apprentissage_critique", "id_semestre", "id_competence"])
        df = df[df["code_competence"] != ""]
        df = df[df["semestre"] != ""]

        if df.empty:
            return []
        return df.to_dict("records")

    @app.callback(
        Output("metier-competence-graph", "figure"),
        Input("metier-ac-store", "data"),
    )
    def update_metier_competence_graph(stored_data):
        if not stored_data:
            return empty_figure("Aucune donnée disponible pour ce métier.")

        df = pd.DataFrame(stored_data)
        if df.empty:
            return empty_figure("Aucune donnée disponible pour ce métier.")

        graph_df = (
            df[["code_competence", "id_apprentissage_critique"]]
            .drop_duplicates(subset=["code_competence", "id_apprentissage_critique"])
            .groupby("code_competence", as_index=False)
            .agg(nb_ac=("id_apprentissage_critique", "nunique"))
            .sort_values("nb_ac", ascending=True)
        )
        if graph_df.empty:
            return empty_figure("Aucune compétence trouvée.")

        fig = px.bar(
            graph_df,
            x="nb_ac",
            y="code_competence",
            orientation="h",
            text="nb_ac",
            color="code_competence",
            color_discrete_map=COLOR_MAP,
            title="Métier visé – Compétences mobilisées",
        )
        fig.update_traces(
            textposition="outside",
            hovertemplate=("Compétence=%{y}<br>Nombre d'AC=%{x}<extra></extra>"),
        )
        fig.update_layout(
            xaxis_title="Nombre d'AC",
            yaxis_title="Compétence",
            showlegend=False,
            margin=dict(l=50, r=20, t=70, b=40),
            height=420,
        )
        return fig

    @app.callback(
        Output("metier-semestre-graph", "figure"),
        Input("metier-ac-store", "data"),
    )
    def update_metier_semestre_graph(stored_data):
        if not stored_data:
            return empty_figure("Aucune donnée disponible pour ce métier.")

        df = pd.DataFrame(stored_data)
        if df.empty:
            return empty_figure("Aucune donnée disponible pour ce métier.")

        graph_df = (
            df[["id_semestre", "semestre", "id_apprentissage_critique"]]
            .drop_duplicates(subset=["id_semestre", "id_apprentissage_critique"])
            .groupby(["id_semestre", "semestre"], as_index=False)
            .agg(nb_ac=("id_apprentissage_critique", "nunique"))
            .sort_values("id_semestre")
        )
        if graph_df.empty:
            return empty_figure("Aucun semestre trouvé.")

        fig = px.bar(
            graph_df,
            x="semestre",
            y="nb_ac",
            text="nb_ac",
            custom_data=["id_semestre"],
            title="Métier visé – Nombre d’AC par semestre",
        )
        fig.update_traces(hovertemplate=("Semestre=%{x}<br>Nombre d'AC=%{y}<extra></extra>"))
        fig.update_layout(
            xaxis_title="Semestre",
            yaxis_title="Nombre d'AC",
            clickmode="event+select",
            showlegend=False,
            margin=dict(l=50, r=20, t=70, b=40),
            height=420,
        )
        return fig

    @app.callback(
        Output("metier-semestre-ac-list", "children"),
        Input("metier-semestre-graph", "clickData"),
        Input("metier-dropdown", "value"),
        State("metier-ac-store", "data"),
        State("metier-dropdown", "options"),
    )
    def update_semestre_ac_list(clickData, selected_metier_id, stored_data, metier_options):
        if not stored_data:
            return default_ac_panel()

        if not clickData or "points" not in clickData or len(clickData["points"]) == 0:
            return default_ac_panel()

        df = pd.DataFrame(stored_data)
        if df.empty:
            return default_ac_panel()

        selected_semestre = clickData["points"][0]["x"]
        df_sem = df[df["semestre"] == selected_semestre].copy()
        if df_sem.empty:
            return default_ac_panel()

        ac_df = (
            df_sem[["id_apprentissage_critique", "libelle_apprentissage", "code_competence"]]
            .dropna(subset=["id_apprentissage_critique", "libelle_apprentissage"])
            .drop_duplicates(subset=["id_apprentissage_critique"])
            .sort_values("id_apprentissage_critique")
        )
        if ac_df.empty:
            return default_ac_panel()

        metier_label = None
        if metier_options and selected_metier_id is not None:
            for opt in metier_options:
                if opt["value"] == selected_metier_id:
                    metier_label = opt["label"]
                    break

        children = [
            html.H4(
                f"Semestre {selected_semestre} — Apprentissages critiques",
                style={"fontWeight": "bold", "marginBottom": "12px"},
            )
        ]
        if metier_label:
            children.append(
                html.P(
                    f"Métier sélectionné : {metier_label}",
                    style={"marginBottom": "15px", "color": "#555"},
                )
            )
        children.append(
            html.Ul(
                [
                    html.Li(
                        f"{row['code_competence']} — {row['libelle_apprentissage']}",
                        style={"marginBottom": "10px"},
                    )
                    for _, row in ac_df.iterrows()
                ],
                style={"paddingLeft": "22px"},
            )
        )
        return html.Div(children)
