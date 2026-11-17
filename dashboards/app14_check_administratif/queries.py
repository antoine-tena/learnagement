from collections import defaultdict

import networkx as nx
import plotly.graph_objects as go

# Couleurs et icônes par type de nœud
NODE_STYLE = {
    "root": {"color": "#4A4E69", "symbol": "diamond", "size": 20},
    "file": {"color": "#3A86FF", "symbol": "square", "size": 16},
    "function": {"color": "#8338EC", "symbol": "circle", "size": 14},
    "table": {"color": "#FB5607", "symbol": "square", "size": 14},
    "field": {"color": "#06D6A0", "symbol": "circle", "size": 12},
    "role": {"color": "#FFB703", "symbol": "star", "size": 12},
}

ACCESS_COLOR = {
    "direct": "#06D6A0",
    "indirect": "#FF6B6B",
    None: "#06D6A0",
}


def build_graph_from_tree(node: dict, G: nx.DiGraph | None = None) -> nx.DiGraph:
    """Construit un DiGraph NetworkX récursivement depuis l'arbre JSON."""
    if G is None:
        G = nx.DiGraph()

    node_id = node["id"]
    node_type = node["type"]
    node_name = node["name"]

    attrs = {
        "label": node_name,
        "type": node_type,
        "access": node.get("access"),
        "exposed_as": node.get("exposed_as"),
    }
    G.add_node(node_id, **attrs)

    for child in node.get("children", []):
        child_id = child["id"]
        G.add_node(child_id)
        G.add_edge(node_id, child_id)
        build_graph_from_tree(child, G)

    return G


def compute_positions(G: nx.DiGraph) -> dict:
    """
    Disposition hiérarchique homogène par niveau (BFS depuis root).
    Retourne {node_id: (x, y)}.
    """
    levels = {}
    for node in nx.topological_sort(G):
        preds = list(G.predecessors(node))
        if not preds:
            levels[node] = 0
        else:
            levels[node] = max(levels[p] for p in preds) + 1

    level_nodes = defaultdict(list)
    for node, lvl in levels.items():
        level_nodes[lvl].append(node)

    pos = {}
    for lvl, nodes in level_nodes.items():
        n = len(nodes)
        for i, node in enumerate(nodes):
            pos[node] = (
                lvl * 3,  # x — espacement horizontal
                -(i - (n - 1) / 2) * 2,  # y — centré verticalement
            )

    return pos


def build_figure(G: nx.DiGraph, pos: dict) -> go.Figure:
    """Construit la figure Plotly depuis le graphe et les positions."""
    edge_x, edge_y = [], []
    for src, dst in G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[dst]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=1, color="#AAAAAA"),
        hoverinfo="none",
    )

    node_traces = []
    by_type = defaultdict(list)

    for node_id, attrs in G.nodes(data=True):
        ntype = attrs.get("type", "field")
        by_type[ntype].append((node_id, attrs))

    for ntype, items in by_type.items():
        style = NODE_STYLE.get(ntype, NODE_STYLE["field"])

        xs, ys, texts, hovers, colors = [], [], [], [], []
        for node_id, attrs in items:
            x, y = pos[node_id]
            xs.append(x)
            ys.append(y)
            texts.append(attrs.get("label", node_id))

            if ntype == "field":
                colors.append(ACCESS_COLOR[attrs.get("access")])
            else:
                colors.append(str(style["color"]))

            hover = f"<b>{attrs.get('label', node_id)}</b><br>type: {ntype}"
            if attrs.get("access"):
                hover += f"<br>access: {attrs['access']}"
            if attrs.get("exposed_as"):
                hover += f"<br>exposed_as: {attrs['exposed_as']}"
            hovers.append(hover)

        node_traces.append(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                name=ntype,
                marker=dict(
                    symbol=style["symbol"],
                    size=style["size"],
                    color=colors,
                    line=dict(width=1, color="#FFFFFF"),
                ),
                text=texts,
                textposition="middle right",
                textfont=dict(size=10),
                hovertext=hovers,
                hoverinfo="text",
            )
        )

    fig = go.Figure(
        data=[edge_trace] + node_traces,
        layout=go.Layout(
            title="DAG — Arbre des droits d'accès",
            showlegend=True,
            hovermode="closest",
            margin=dict(l=20, r=20, t=50, b=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="#1E1E2E",
            paper_bgcolor="#1E1E2E",
            font=dict(color="#FFFFFF"),
            legend=dict(
                title="Type de nœud",
                bgcolor="#2A2A3E",
                bordercolor="#444",
                borderwidth=1,
            ),
        ),
    )
    return fig
