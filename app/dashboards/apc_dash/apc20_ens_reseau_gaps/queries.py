from io import StringIO

import networkx as nx
import pandas as pd
import plotly.graph_objects as go

from ..apc20_layout import COLORS, empty_fig, get_competence_color


def build_reseau_figure(competences, raw_data, clicked_mod):
    if not competences or raw_data is None:
        return empty_fig("Données non disponibles")

    df_main = pd.read_json(StringIO(raw_data["df_main"]), orient="split")
    module_names = raw_data.get("module_names", {})

    df_f = df_main[df_main["competence_label"].isin(competences)].copy()
    df_f = df_f[df_f["id_module"] != 0]

    if df_f.empty:
        return empty_fig("Aucun module pour les compétences sélectionnées")

    mod_acs = df_f.groupby("id_module")["id_apprentissage_critique"].apply(set).to_dict()

    mod_dom_comp = (
        df_f.groupby(["id_module", "competence_label"])["id_apprentissage_critique"]
        .nunique()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
        .drop_duplicates("id_module")
        .set_index("id_module")["competence_label"]
        .to_dict()
    )

    G = nx.Graph()
    modules = list(mod_acs.keys())
    for mod in modules:
        G.add_node(mod, n_ac=len(mod_acs[mod]))

    for i in range(len(modules)):
        for j in range(i + 1, len(modules)):
            shared = mod_acs[modules[i]] & mod_acs[modules[j]]
            if shared:
                G.add_edge(modules[i], modules[j], weight=len(shared))

    if not G.nodes():
        return empty_fig("Aucun module à afficher")

    pos = nx.spring_layout(G, seed=42, k=3.0)

    def _mod_label(m):
        raw = module_names.get(str(int(m)), module_names.get(str(m), f"M{m}"))
        return str(raw)[:30]

    if clicked_mod is not None and clicked_mod not in G.nodes():
        clicked_mod = None

    neighbors = set(G.neighbors(clicked_mod)) if clicked_mod is not None else set()

    edge_traces = _build_edge_traces(G, pos, clicked_mod)
    node_traces = _build_node_traces(
        G, pos, competences, mod_dom_comp, clicked_mod, neighbors, _mod_label
    )

    if clicked_mod is not None and clicked_mod in pos:
        focus = list(neighbors | {clicked_mod})
        xs = [pos[n][0] for n in focus]
        ys = [pos[n][1] for n in focus]
        pad = 0.6
        xaxis_cfg = dict(
            range=[min(xs) - pad, max(xs) + pad],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        )
        yaxis_cfg = dict(
            range=[min(ys) - pad, max(ys) + pad],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
        )
        title_text = f"{_mod_label(clicked_mod)} — {G.degree(clicked_mod)} connexion(s)"
    else:
        xaxis_cfg = dict(showgrid=False, zeroline=False, showticklabels=False)
        yaxis_cfg = dict(showgrid=False, zeroline=False, showticklabels=False)
        title_text = "Réseau de modules — liens par apprentissages critiques partagés"

    fig = go.Figure(data=edge_traces + node_traces)
    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.5,
            xanchor="center",
            font=dict(size=14, family="Inter, sans-serif"),
        ),
        showlegend=True,
        legend=dict(title="Compétence dominante", font=dict(size=11)),
        height=560,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=xaxis_cfg,
        yaxis=yaxis_cfg,
        margin=dict(l=20, r=20, t=70, b=20),
        font=dict(family="Inter, sans-serif"),
        hovermode="closest",
    )
    return fig


def _build_edge_traces(G, pos, clicked_mod):
    edge_traces = []
    if clicked_mod is not None:
        dim_x, dim_y, hi_x, hi_y = [], [], [], []
        for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            if u == clicked_mod or v == clicked_mod:
                hi_x += [x0, x1, None]
                hi_y += [y0, y1, None]
            else:
                dim_x += [x0, x1, None]
                dim_y += [y0, y1, None]
        if dim_x:
            edge_traces.append(
                go.Scatter(
                    x=dim_x,
                    y=dim_y,
                    mode="lines",
                    line=dict(width=0.4, color="#EBEBEB"),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
        if hi_x:
            edge_traces.append(
                go.Scatter(
                    x=hi_x,
                    y=hi_y,
                    mode="lines",
                    line=dict(width=2.5, color=COLORS["primary"]),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
    else:
        ex, ey = [], []
        for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            ex += [x0, x1, None]
            ey += [y0, y1, None]
        edge_traces.append(
            go.Scatter(
                x=ex,
                y=ey,
                mode="lines",
                line=dict(width=0.8, color="#D1D5DB"),
                hoverinfo="none",
                showlegend=False,
            )
        )
    return edge_traces


def _build_node_traces(G, pos, competences, mod_dom_comp, clicked_mod, neighbors, mod_label_fn):
    seen_comps = set()
    node_traces = []

    for comp in competences:
        comp_mods = [m for m in G.nodes() if mod_dom_comp.get(m) == comp]
        for m in comp_mods:
            is_clicked = clicked_mod is not None and m == clicked_mod
            is_neighbor = m in neighbors
            is_dimmed = clicked_mod is not None and not is_clicked and not is_neighbor

            base_size = max(14, min(45, G.nodes[m]["n_ac"] * 3))
            size = base_size + 14 if is_clicked else base_size
            opacity = 0.15 if is_dimmed else 0.88
            border_w = 3.5 if is_clicked else (2 if is_neighbor else 1.5)
            border_c = (
                "#1D4ED8" if is_clicked else ("white" if not is_neighbor else COLORS["primary"])
            )
            txt_color = "#D1D5DB" if is_dimmed else "#374151"
            txt_size = 11 if is_clicked else 9

            hover = (
                f"<b>{mod_label_fn(m)}</b><br>"
                f"AC couverts : {G.nodes[m]['n_ac']}<br>"
                f"Compétence dominante : {comp}<br>"
                f"Connexions : {G.degree(m)}"
            )
            if is_clicked and neighbors:
                lines = [
                    f"  • {mod_label_fn(nb)} — {G.edges[m, nb]['weight']} AC partagés"
                    for nb in sorted(neighbors, key=lambda n: -G.edges[m, n]["weight"])
                ]
                hover += "<br><br><b>Modules voisins :</b><br>" + "<br>".join(lines)

            first_of_comp = comp not in seen_comps
            if first_of_comp:
                seen_comps.add(comp)

            node_traces.append(
                go.Scatter(
                    x=[pos[m][0]],
                    y=[pos[m][1]],
                    mode="markers+text",
                    marker=dict(
                        size=size,
                        color=get_competence_color(comp),
                        opacity=opacity,
                        line=dict(width=border_w, color=border_c),
                    ),
                    text=[mod_label_fn(m)],
                    textposition="top center",
                    textfont=dict(size=txt_size, color=txt_color),
                    name=comp,
                    legendgroup=comp,
                    showlegend=first_of_comp,
                    hovertext=[hover],
                    hoverinfo="text",
                    customdata=[m],
                )
            )
    return node_traces
