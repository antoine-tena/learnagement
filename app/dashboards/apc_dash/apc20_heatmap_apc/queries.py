import pandas as pd
import plotly.graph_objects as go

COLORS = {
    "primary": "#3B82F6",
    "light": "#F8FAFC",
    "competences": {
        "COMP_IDU1": "#FF513F",
        "COMP_IDU2": "#FFA03F",
        "COMP_IDU3": "#3B82F6",
        "COMP_IDU4": "#10B981",
    },
}

KNOWN_COMPETENCES = ["COMP_IDU1", "COMP_IDU2", "COMP_IDU3", "COMP_IDU4"]
KNOWN_NIVEAUX = [1, 2, 3]
KNOWN_TYPES_LIEN = ["Requis", "Recommandé", "Complémentaire"]


def get_competence_color(comp):
    return COLORS["competences"].get(comp, "#777777")


def parse_competencies(row):
    if "niveau_code" in row.index and pd.notna(row["niveau_code"]):
        return row["niveau_code"]
    return None


def compute_competency_counts_per_module(df_input):
    df_work = df_input.copy()
    if "libelle_apprentissage" not in df_work.columns:
        df_work = df_work.assign(libelle_apprentissage=df_work.index.astype(str))

    df_work = df_work.assign(All_Competencies=df_work["niveau_code"])
    df_exploded = df_work.copy()

    df_pivot_global = (
        df_exploded.groupby(["niveau", "competence_label"], as_index=False)
        .size()
        .pivot(index="niveau", columns="competence_label", values="size")
        .fillna(0)
        .astype("Float64")
    )

    df_count = df_exploded.groupby(
        ["niveau", "id_module", "competence_label"], as_index=False
    ).size()

    df_pivot_niveau = (
        df_count.pivot(index=["niveau", "id_module"], columns="competence_label", values="size")
        .fillna(0)
        .astype("Float64")
    )

    df_pivot_module = df_exploded.pivot(
        index=["niveau", "id_module", "libelle_apprentissage"],
        columns="competence_label",
        values="type_lien",
    ).fillna("")

    return df_pivot_global, df_pivot_niveau, df_pivot_module


def create_heatmap_for_global(df_pivot_global):
    fig = go.Figure()
    for j in range(df_pivot_global.shape[1]):
        comp = df_pivot_global.columns[j]
        color_scale = ["white", get_competence_color(comp)]
        df_comp = df_pivot_global.copy()
        for col in df_comp.columns:
            if col != comp:
                df_comp.loc[:, col] = pd.NA
        fig.add_trace(
            go.Heatmap(
                z=df_comp.values,
                x=df_pivot_global.columns,
                y=df_pivot_global.index,
                colorscale=color_scale,
                showscale=False,
                hoverongaps=False,
                hovertemplate="<b>Niveau %{y}</b><br>%{x}<br>AC: %{z}<extra></extra>",
            )
        )
    fig.update_layout(
        title=dict(
            text="Répartition des compétences<br>"
            "<sub>Cliquez sur un niveau pour voir les modules</sub>",
            x=0.5,
            xanchor="center",
            font=dict(size=20, family="Inter, sans-serif"),
        ),
        xaxis_title="Compétences",
        xaxis=dict(tickangle=-45, tickfont=dict(size=11)),
        yaxis_title="Niveaux",
        yaxis=dict(type="category", autorange="reversed", showgrid=False, tickfont=dict(size=12)),
        height=600,
        font=dict(size=11, family="Inter, sans-serif"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=100, r=60, t=120, b=150),
        clickmode="event+select",
    )
    return fig


def create_heatmap_for_niveau(niveau, df_pivot_niveau, module_names):
    df_used = df_pivot_niveau.xs(niveau, level="niveau")
    fig = go.Figure()
    z_max = df_pivot_niveau.max().max()

    module_names_list = [
        module_names.get(
            mod,
            module_names.get(float(mod) if not isinstance(mod, float) else mod, f"Module {mod}"),
        )
        for mod in df_used.index
    ]
    # customdata : ID du module pour chaque cellule (utilisé par le callback pour le drill-down)
    module_ids_customdata = [[str(mod)] * len(df_used.columns) for mod in df_used.index]

    for j in range(df_used.shape[1]):
        comp = df_used.columns[j]
        color_scale = ["white", get_competence_color(comp)]
        df_comp = df_used.copy()
        for col in df_comp.columns:
            if col != comp:
                df_comp.loc[:, col] = pd.NA
        fig.add_trace(
            go.Heatmap(
                z=df_comp.values,
                x=df_used.columns,
                y=module_names_list,
                zmin=0,
                zmax=z_max,
                colorscale=color_scale,
                showscale=False,
                hoverongaps=False,
                xgap=1,
                ygap=1,
                customdata=module_ids_customdata,
                hovertemplate="<b>%{y}</b><br>%{x}<br>AC: %{z}<extra></extra>",
            )
        )
    fig.update_layout(
        title=dict(
            text=f"Modules du niveau {niveau}<br>"
            "<sub>Cliquez sur un module pour voir les apprentissages critiques</sub>",
            x=0.5,
            xanchor="center",
            font=dict(size=20, family="Inter, sans-serif"),
        ),
        xaxis_title="Compétences",
        yaxis_title="Modules",
        xaxis=dict(tickangle=-45, tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11)),
        height=max(500, len(df_used.index) * 35 + 180),
        font=dict(size=11, family="Inter, sans-serif"),
        plot_bgcolor="white",
        paper_bgcolor=COLORS["light"],
        margin=dict(l=280, r=60, t=120, b=180),
        clickmode="event+select",
    )
    return fig


def create_heatmap_for_module(module_id, df_pivot_module, module_names):
    df_reorganized = df_pivot_module.replace(
        {"Requis": 3, "Recommandé": 2, "Complémentaire": 1, "Non associé": 0, "": 0}
    )
    df_used = df_reorganized.xs(module_id, level="id_module").astype("Int64")
    fig = go.Figure()

    for j in range(df_used.shape[1]):
        comp = df_used.columns[j]
        color_scale = ["white", get_competence_color(comp)]
        df_comp = df_used.copy()
        for col in df_comp.columns:
            if col != comp:
                df_comp.loc[:, col] = pd.NA
        hover_text = [idx[-1] if isinstance(idx, tuple) else idx for idx in df_used.index]
        fig.add_trace(
            go.Heatmap(
                z=df_comp.values,
                x=df_used.columns,
                y=hover_text,
                zmin=0,
                zmax=3,
                colorscale=color_scale,
                showscale=False,
                hoverongaps=False,
                xgap=1,
                ygap=1,
                customdata=df_comp.values,
                hovertemplate="<b>%{y}</b><br>%{x}<br>Type: %{customdata}<extra></extra>",
            )
        )

    module_name = module_names.get(
        module_id,
        module_names.get(
            float(module_id) if not isinstance(module_id, float) else module_id,
            f"Module {module_id}",
        ),
    )
    fig.update_layout(
        title=dict(
            text=f"{module_name} — Apprentissages critiques",
            x=0.5,
            xanchor="center",
            font=dict(size=20, family="Inter, sans-serif"),
        ),
        xaxis_title="Compétences",
        yaxis_title="Apprentissages critiques",
        xaxis=dict(tickangle=-45, tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=10)),
        height=max(600, len(df_used.index) * 25 + 180),
        font=dict(size=11, family="Inter, sans-serif"),
        plot_bgcolor="white",
        paper_bgcolor=COLORS["light"],
        margin=dict(l=400, r=60, t=120, b=180),
    )
    return fig


def _empty_fig(msg="Chargement des données..."):
    fig = go.Figure()
    fig.add_annotation(
        text=msg,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=14, color="#94a3b8"),
    )
    fig.update_layout(height=500, paper_bgcolor="white", plot_bgcolor="white")
    return fig
