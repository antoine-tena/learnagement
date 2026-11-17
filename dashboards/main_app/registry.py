"""Registre des applications Dash, icônes et menus par rôle."""

icon_map = {
    "app2": "fa-solid fa-chart-pie",
    "app3": "fa-solid fa-user-minus",
    "app4": "fa-solid fa-user-graduate",
    "app5": "fa-solid fa-chalkboard-teacher",
    "app7": "fa-solid fa-briefcase",
    "app8": "fa-solid fa-book",
    "app9": "fa-solid fa-tasks",
    "app10": "fa-solid fa-percentage",
    "apc_ens_dashboard": "fa-solid fa-graduation-cap",
    "connected": "fa-solid fa-check",
    "disconnected": "fa-solid fa-xmark",
    "apc20_hub": "fa-solid fa-graduation-cap",
    "dashboard": "fa-solid fa-terminal",
    "exit": "fa-solid fa-arrow-right-from-bracket",
}


def import_apps():
    """Importe les layouts et callbacks de toutes les applications Dash."""
    from apc_dash.apc_hub import apc_hub_layout, register_apc_hub_callbacks
    from pages.competences import (
        app2_layout,
        register_callbacks as register_callbacks_app2,
    )
    from pages.absences_administratif import (
        app3_administratif_layout,
        register_callbacks as register_callbacks_app3_administratif,
    )
    from pages.absences_enseignant import (
        app3_enseignant_layout,
        register_callbacks as register_callbacks_app3_enseignant,
    )
    from pages.absences_etudiant import (
        app3_etudiant_layout,
        register_callbacks as register_callbacks_app3_etudiant,
    )
    from pages.notes_etudiant import (
        app4_etudiant_layout,
        register_callbacks as register_callbacks_app4_etudiant,
    )
    from pages.notes_enseignant import (
        app4_enseignant_layout,
        register_callbacks as register_callbacks_app4_enseignant,
    )
    from pages.modules_enseignant_edit import (
        app5_enseignant_edit_layout,
        register_callbacks_edit as register_callbacks_app5_enseignant_edit,
    )
    from pages.modules_enseignant_view import (
        app5_enseignant_view_layout,
        register_callbacks_view as register_callbacks_app5_enseignant_view,
    )
    from pages.charge_administratif import (
        app7_administratif_layout,
        register_callbacks as register_callbacks_app7_administratif,
    )
    from pages.charge_enseignant import (
        app7_enseignant_layout,
        register_callbacks as register_callbacks_app7_enseignant,
    )
    from pages.charge_etudiant import (
        app7_etudiant_layout,
        register_callbacks as register_callbacks_app7_etudiant,
    )
    from pages.rendus_etudiant import app9_layout, register_callbacks as register_callbacks_app9
    from pages.stages_administratif import (
        app10_administratif_layout,
        register_callbacks as register_callbacks_app10_administratif,
    )
    from pages.stages_enseignant import (
        app10_enseignant_layout,
        register_callbacks as register_callbacks_app10_enseignant,
    )
    from pages.stages_etudiant import (
        app10_etudiant_layout,
        register_callbacks as register_callbacks_app10_etudiant,
    )
    from pages.dependances import app11_layout, register_callbacks as register_callbacks_app11
    from pages.dependances_new import (
        app11_new_layout,
        register_callbacks as register_callbacks_app11_new,
    )
    from pages.mccc_administratif import (
        app13_administratif_layout,
        register_callbacks as register_callbacks_app13_administratif,
    )
    from pages.checks_administratif import (
        app14_administratif_layout,
        register_callbacks as register_callbacks_app14_administratif,
    )

    return {
        "app2": (app2_layout, register_callbacks_app2),
        "app3_administratif": (app3_administratif_layout, register_callbacks_app3_administratif),
        "app3_enseignant": (app3_enseignant_layout, register_callbacks_app3_enseignant),
        "app3_etudiant": (app3_etudiant_layout, register_callbacks_app3_etudiant),
        "app4_enseignant": (app4_enseignant_layout, register_callbacks_app4_enseignant),
        "app4_etudiant": (app4_etudiant_layout, register_callbacks_app4_etudiant),
        "app5_enseignant_view": (
            app5_enseignant_view_layout,
            register_callbacks_app5_enseignant_view,
        ),
        "app5_enseignant_edit": (
            app5_enseignant_edit_layout,
            register_callbacks_app5_enseignant_edit,
        ),
        "app7_administratif": (app7_administratif_layout, register_callbacks_app7_administratif),
        "app7_enseignant": (app7_enseignant_layout, register_callbacks_app7_enseignant),
        "app7_etudiant": (app7_etudiant_layout, register_callbacks_app7_etudiant),
        "app9": (app9_layout, register_callbacks_app9),
        "app10_administratif": (app10_administratif_layout, register_callbacks_app10_administratif),
        "app10_enseignant": (app10_enseignant_layout, register_callbacks_app10_enseignant),
        "app10_etudiant": (app10_etudiant_layout, register_callbacks_app10_etudiant),
        "app11": (app11_layout, register_callbacks_app11),
        "app11_new": (app11_new_layout, register_callbacks_app11_new),
        "app13_administratif": (app13_administratif_layout, register_callbacks_app13_administratif),
        "app14_administratif": (app14_administratif_layout, register_callbacks_app14_administratif),
        "apc20_hub": (apc_hub_layout, register_apc_hub_callbacks),
    }


def build_menu_items(environment: str | None) -> dict[str, list[tuple[str, str]]]:
    """Construit le menu latéral par rôle selon l'environnement."""
    menu_items: dict[str, list[tuple[str, str]]] = {
        "administratif": [
            ("Absences", "app3_administratif"),
            ("Gestion des stages", "app10_administratif"),
            ("MCCC", "app13_administratif"),
            ("Check", "app14_administratif"),
            ("Charge enseignant", "app7_administratif"),
            ("Approche par compétences", "apc20_hub"),
        ],
        "enseignant": [
            ("Vue modules", "app5_enseignant_view"),
            ("MaJ modules", "app5_enseignant_edit"),
            ("Dépendance Séances", "app11"),
            ("MaJ Dépendance Séances", "app11_new"),
            ("Absences", "app3_enseignant"),
            ("Notes", "app4_enseignant"),
            ("Charge de travail", "app7_enseignant"),
            ("Tutorat stages", "app10_enseignant"),
            ("Approche par compétences", "apc20_hub"),
        ],
        "etudiant": [
            ("Stages", "app10_etudiant"),
        ],
    }

    if environment == "dev":
        menu_items["etudiant"] += [
            ("Compétences", "app2"),
            ("Absences", "app3_etudiant"),
            ("Notes", "app4_etudiant"),
            ("Dépendance Séances", "app11"),
            ("Charge de travail", "app7_etudiant"),
            ("Avancement rendus", "app9"),
            ("Approche par compétences", "apc20_hub"),
        ]

    return menu_items
