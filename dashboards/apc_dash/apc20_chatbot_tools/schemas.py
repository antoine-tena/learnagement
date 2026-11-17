"""Schémas JSON des outils disponibles pour le chatbot APC (API Gemini)."""

GEMINI_TOOLS = [
    {
        "name": "lister_modules",
        "description": (
            "Liste tous les modules de la formation avec leur identifiant, code et nom. "
            "Utilise cet outil pour connaître les modules disponibles ou pour trouver "
            "l'identifiant d'un module avant d'appeler un autre outil."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "lister_competences",
        "description": "Liste toutes les compétences du référentiel APC avec leur code et libellé.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "lister_ac",
        "description": (
            "Liste tous les apprentissages critiques (AC) du référentiel avec leur libellé, "
            "la compétence associée et le niveau (N1, N2, N3). "
            "Utilise cet outil pour trouver l'identifiant d'un AC."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "lister_ac_du_module",
        "description": (
            "Liste les apprentissages critiques couverts par un module spécifique, "
            "avec le type de lien (Requis, Recommandé, Complémentaire), "
            "la compétence associée et le niveau."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id_module": {
                    "type": "number",
                    "description": "Identifiant numérique du module (obtenu via lister_modules)",
                }
            },
            "required": ["id_module"],
        },
    },
    {
        "name": "lister_modules_dun_ac",
        "description": (
            "Liste tous les modules qui couvrent un apprentissage critique donné, "
            "avec le type de lien (Requis, Recommandé, Complémentaire)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "id_ac": {
                    "type": "number",
                    "description": "Identifiant numérique de l'apprentissage critique (obtenu via lister_ac)",
                }
            },
            "required": ["id_ac"],
        },
    },
    {
        "name": "ac_sans_module_requis",
        "description": (
            "Retourne la liste des apprentissages critiques qui n'ont aucun module "
            "avec un lien de type 'Requis'. Ce sont les trous du référentiel APC."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "modules_sans_ac_requis",
        "description": (
            "Retourne la liste des modules qui n'ont aucun apprentissage critique "
            "avec un lien de type 'Requis'. Ce sont les modules à ancrage APC faible."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "statistiques_globales",
        "description": (
            "Retourne des statistiques globales sur le référentiel APC : "
            "nombre de modules, compétences, AC, taux de couverture, nombre de trous."
        ),
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "couverture_competence",
        "description": (
            "Analyse la couverture d'une compétence spécifique : pour chaque niveau "
            "(N1, N2, N3), liste les AC et combien de modules les couvrent."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code_competence": {
                    "type": "string",
                    "description": "Code de la compétence (ex: COMP_IDU1, COMP_IDU2...)",
                }
            },
            "required": ["code_competence"],
        },
    },
]
