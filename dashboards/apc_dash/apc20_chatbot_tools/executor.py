"""Routeur d'exécution des outils du chatbot APC."""

from .handlers import (
    _ac_sans_module_requis,
    _couverture_competence,
    _lister_ac,
    _lister_ac_du_module,
    _lister_competences,
    _lister_modules,
    _lister_modules_dun_ac,
    _modules_sans_ac_requis,
    _statistiques_globales,
)


def execute_tool(name: str, inputs: dict, token: str) -> str:
    try:
        if name == "lister_modules":
            return _lister_modules(token)
        elif name == "lister_competences":
            return _lister_competences(token)
        elif name == "lister_ac":
            return _lister_ac(token)
        elif name == "lister_ac_du_module":
            return _lister_ac_du_module(token, inputs["id_module"])
        elif name == "lister_modules_dun_ac":
            return _lister_modules_dun_ac(token, inputs["id_ac"])
        elif name == "ac_sans_module_requis":
            return _ac_sans_module_requis(token)
        elif name == "modules_sans_ac_requis":
            return _modules_sans_ac_requis(token)
        elif name == "statistiques_globales":
            return _statistiques_globales(token)
        elif name == "couverture_competence":
            return _couverture_competence(token, inputs["code_competence"])
        else:
            return f"Outil inconnu : {name}"
    except Exception as e:
        return f"Erreur lors de l'exécution de l'outil '{name}' : {e}"
