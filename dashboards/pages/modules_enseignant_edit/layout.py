from dash import dcc, html

app5_enseignant_edit_layout = html.Div(
    [
        html.H1(id="app5_ens_edit_title", children="Séquençage"),
        dcc.Dropdown(
            id="filtre_module",
            options=[],
            placeholder="Sélectionnez un module",
        ),
        html.Div(
            [
                html.Label("Add Séquencage :"),
                html.Div(id="add_sequencage_div"),
            ]
        ),
        html.Button("Add", id="add_sequencage_button", n_clicks=0),
        html.Label("", id="sequencage_info_status"),
        html.Div(
            [
                html.Label("Séquencage :"),
                html.Div(id="sequencage_div"),
            ]
        ),
        html.Div(
            [
                html.Label("Séquencage vs Maquette :"),
                html.Div(id="sequencage_vs_maquette_div"),
            ]
        ),
        html.H1(children="Séances"),
        dcc.Dropdown(
            id="filtre_type",
            options=[],
            placeholder="Sélectionnez un type de séance",
        ),
        html.Div(
            [
                html.Label("Séances :"),
                html.Div(id="sequence_div"),
            ]
        ),
        html.H1(children="Session"),
        dcc.Dropdown(
            id="filtre_promo",
            options=[],
            placeholder="Sélectionnez une promotion",
        ),
        html.Div(
            [
                html.Label("Session :"),
                html.Div(id="session_div"),
            ]
        ),
    ]
)
