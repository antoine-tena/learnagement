"""Requêtes API et préparation des graphiques et listes AC / CE."""

from app_tools import get_endpoint, get_python_backend_url
from dash import html
import pandas as pd
import plotly.express as px

from .layout import COLOR_MAP


def load_competence_graph_data(
    token: str,
    endpoint_path: str,
    id_col: str,
    label_col: str,
    count_col: str,
    graph_title: str,
):
    """Charge les données AC ou CE depuis le backend et construit la figure + options."""
    url = get_python_backend_url(endpoint_path)
    df = get_endpoint(url, token=token)

    if df is None or len(df) == 0:
        return [], {}, [], None

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    if df.empty:
        return [], {}, [], None

    df = df.copy()
    required_cols = ["code_competence", "libelle_competence", id_col, label_col]
    for col in required_cols:
        if col not in df.columns:
            return [], {}, [], None

    df["code_competence"] = df["code_competence"].fillna("").astype(str).str.strip()
    df["libelle_competence"] = df["libelle_competence"].fillna("").astype(str).str.strip()
    df[label_col] = df[label_col].fillna("").astype(str).str.strip()

    df = df.dropna(subset=[id_col])
    df = df[df["code_competence"] != ""]

    if df.empty:
        return [], {}, [], None

    comp_df = (
        df[["code_competence", "libelle_competence"]]
        .drop_duplicates(subset=["code_competence"])
        .sort_values("code_competence")
    )

    options = [
        {
            "label": f"{row['code_competence']} - {row['libelle_competence']}",
            "value": row["code_competence"],
        }
        for _, row in comp_df.iterrows()
    ]
    default_value = options[0]["value"] if options else None

    graph_df = (
        df[["code_competence", "libelle_competence", id_col]]
        .drop_duplicates(subset=["code_competence", id_col])
        .groupby(["code_competence", "libelle_competence"], as_index=False)
        .agg(**{count_col: (id_col, "nunique")})
        .sort_values(count_col, ascending=True)
    )

    fig = px.bar(
        graph_df,
        x=count_col,
        y="code_competence",
        orientation="h",
        text=count_col,
        color="code_competence",
        color_discrete_map=COLOR_MAP,
        custom_data=["libelle_competence"],
        title=graph_title,
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            f"compétence=%{{y}}<br>{count_col}=%{{x}}<br>libellé=%{{customdata[0]}}<extra></extra>"
        ),
    )
    fig.update_layout(
        xaxis_title=count_col,
        yaxis_title="code_competence",
        clickmode="event+select",
        showlegend=False,
        margin=dict(l=40, r=20, t=70, b=40),
        height=520,
    )

    return df.to_dict("records"), fig, options, default_value


def build_detail_list(
    selected_competence: str | None,
    stored_data: list[dict] | None,
    id_col: str,
    label_col: str,
    section_label: str,
    empty_message: str,
):
    """Construit la liste HTML des AC ou CE associés à une compétence sélectionnée."""
    if not selected_competence:
        return "Choisissez une compétence"

    if not stored_data:
        return "Aucune donnée disponible"

    df = pd.DataFrame(stored_data)
    if df.empty:
        return "Aucune donnée disponible"

    df_filtre = df[df["code_competence"] == selected_competence].copy()
    if df_filtre.empty:
        return f"Aucune donnée pour {selected_competence}"

    item_df = df_filtre[[id_col, label_col]].dropna(subset=[id_col, label_col]).copy()
    item_df[label_col] = item_df[label_col].astype(str).str.strip()
    item_df = item_df[item_df[label_col] != ""]
    item_df = item_df.drop_duplicates(subset=[id_col]).sort_values(id_col)

    if item_df.empty:
        return html.Div(
            [
                html.H4(f"{selected_competence} — {section_label}"),
                html.P(empty_message),
            ]
        )

    return html.Div(
        [
            html.H4(
                f"{selected_competence} — {section_label}",
                style={"fontWeight": "bold", "marginBottom": "15px"},
            ),
            html.Ul(
                [
                    html.Li(row[label_col], style={"marginBottom": "10px"})
                    for _, row in item_df.iterrows()
                ],
                style={"paddingLeft": "22px"},
            ),
        ]
    )
