import logging

from pages import checks_tools
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State

from .queries import build_figure, build_graph_from_tree, compute_positions


def register_callbacks(app):
    @app.callback(
        Output("collapse1", "is_open"),
        [Input("collapse-button1", "n_clicks")],
        [State("collapse1", "is_open")],
    )
    def toggle_collapse1(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse2", "is_open"),
        [Input("collapse-button2", "n_clicks")],
        [State("collapse2", "is_open")],
    )
    def toggle_collapse2(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse3", "is_open"),
        [Input("collapse-button3", "n_clicks")],
        [State("collapse3", "is_open")],
    )
    def toggle_collapse3(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse4", "is_open"),
        [Input("collapse-button4", "n_clicks")],
        [State("collapse4", "is_open")],
    )
    def toggle_collapse4(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse5", "is_open"),
        [Input("collapse-button5", "n_clicks")],
        [State("collapse5", "is_open")],
    )
    def toggle_collapse5(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse6", "is_open"),
        [Input("collapse-button6", "n_clicks")],
        [State("collapse6", "is_open")],
    )
    def toggle_collapse6(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse7", "is_open"),
        [Input("collapse-button7", "n_clicks")],
        [State("collapse7", "is_open")],
    )
    def toggle_collapse7(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse8", "is_open"),
        [Input("collapse-button8", "n_clicks")],
        [State("collapse8", "is_open")],
    )
    def toggle_collapse8(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("collapse9", "is_open"),
        [Input("collapse-button9", "n_clicks")],
        [State("collapse9", "is_open")],
    )
    def toggle_collapse9(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output(component_id="table_sequencage_vs_maquette", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_sequencage_vs_maquette(user_id_fake, token):
        df = checks_tools.check_sequencage_vs_maquette(token)
        table_sequencage_vs_maquette = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        return [table_sequencage_vs_maquette]

    @app.callback(
        Output(component_id="table_session_vs_maquette", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_session_vs_maquette(user_id_fake, token):
        df = checks_tools.check_session_vs_maquette(token)
        if df.empty:
            df = pd.DataFrame(columns=["truc", "bidule"])
        table_session_vs_maquette = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        return [table_session_vs_maquette]

    @app.callback(
        Output(component_id="table_modules_sans_ue", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_modules_sans_ue(user_id_fake, token):
        df = checks_tools.check_module_without_learning_unit(token)
        table_modules_sans_ue = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        return [table_modules_sans_ue]

    @app.callback(
        Output(component_id="table_modules_sans_ac", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_modules_sans_ac(user_id_fake, token):
        df = checks_tools.check_module_without_apprentissage_critique(token)
        table_modules_sans_ac = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        return [table_modules_sans_ac]

    @app.callback(
        Output(component_id="div_enseignant_sans_cours", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_enseignant_sans_cours(user_id_fake, token):
        df = checks_tools.check_enseignant_sans_cours(token)
        table_enseignant_sans_cours = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        return [table_enseignant_sans_cours]

    @app.callback(
        Output(component_id="div_session_sans_enseignant", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_session_sans_enseignant(user_id_fake, token):
        df = checks_tools.check_session_sans_enseignant(token)
        table_session_sans_enseignant = dbc.Table.from_dataframe(
            df, striped=True, bordered=True, hover=True
        )
        return [table_session_sans_enseignant]

    @app.callback(
        Output(component_id="div_modules_ects", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_modules_ects(user_id_fake, token):
        df = checks_tools.check_module_ects(token)
        table_modules_ects = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
        return [table_modules_ects]

    @app.callback(
        Output(component_id="div_session_corruption", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_session_corruption(user_id_fake, token):
        df = checks_tools.check_session_corruption(token)
        if not df.empty:
            table_session_corruption = dbc.Table.from_dataframe(
                df, striped=True, bordered=True, hover=True
            )
            return [table_session_corruption]
        return [html.Label("No data available")]

    @app.callback(
        Output(component_id="div_auth", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_auth(user_id_fake, token):
        df = checks_tools.get_access_auth(token)
        logging.info(df)
        if not df.empty:
            table_access_auth = dbc.Table.from_dataframe(
                df, striped=True, bordered=True, hover=True
            )
            logging.info(table_access_auth)
            return [table_access_auth]
        return [html.Label("No data available")]

    @app.callback(
        Output(component_id="div_auth_tree_sqlglot", component_property="children"),
        Input(component_id="fake", component_property="value"),
        State(component_id="token", component_property="data"),
    )
    def display_tree_sqlglot(user_id_fake, token):
        data = checks_tools.get_access_auth_tree_sqlglot(token)
        logging.info(data)

        if not data:
            return [html.Label("No data available")]

        tree = data
        try:
            G = build_graph_from_tree(tree)
            pos = compute_positions(G)
            fig = build_figure(G, pos)

            return [
                dcc.Graph(
                    figure=fig,
                    style={"height": "85vh"},
                    config={"scrollZoom": True, "displayModeBar": True},
                )
            ]

        except Exception as e:
            logging.info(f"Erreur construction DAG : {e}", exc_info=True)
            return [html.Label(f"Erreur : {e}")]
