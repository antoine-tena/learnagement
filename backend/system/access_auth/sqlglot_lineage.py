"""Analyse SQL via sqlglot et construction de l'arbre de data lineage."""

import sqlglot
import sqlglot.expressions as exp


def is_direct_wrapper(node: exp.Expression) -> bool:
    """
    Retourne True si le nœud est une simple transformation
    qui expose directement le champ sous-jacent :
    CAST, ROUND, FLOOR, CEIL, COALESCE à 1 arg, alias simple...
    """
    direct_wrappers = {
        exp.Cast,
        exp.Round,
        exp.Floor,
        exp.Ceil,
        exp.Upper,
        exp.Lower,
        exp.Trim,
        exp.Coalesce,
        exp.TryCast,
    }
    return type(node) in direct_wrappers


def classify_column_in_expression(col: exp.Column, root_expr: exp.Expression) -> str:
    """
    Détermine si une colonne dans une expression est accédée
    de manière 'direct' ou 'indirect'.

    Logique :
    - Si la colonne est l'enfant direct (ou via wrapper direct) → 'direct'
    - Si la colonne est imbriquée dans une fonction d'agrégation,
      une sous-requête, ou une expression arithmétique → 'indirect'
    """
    parent = col.parent

    # Wrapper direct (CAST, ROUND simple, etc.)
    if parent is not None and is_direct_wrapper(parent):
        # Vérifie que c'est le seul argument significatif
        col_siblings = [
            c
            for c in parent.args.values()
            if isinstance(c, (exp.Expression,)) and not isinstance(c, exp.DataType)
        ]
        if len(col_siblings) == 1:
            return "direct"

    # Colonne directe sans transformation
    if isinstance(parent, exp.Alias) or parent is root_expr:
        return "direct"

    # Fonctions d'agrégation → indirect
    aggregate_functions = {
        exp.Sum,
        exp.Avg,
        exp.Max,
        exp.Min,
        exp.Count,
        exp.StddevPop,
        exp.VariancePop,
    }
    # Remontée manuelle vers la racine
    node = col.parent
    while node is not None and node is not root_expr:
        if type(node) in aggregate_functions:
            return "indirect"
        if isinstance(node, exp.Subquery):
            return "indirect"
        if isinstance(node, (exp.Add, exp.Sub, exp.Mul, exp.Div)):
            return "indirect"
        if isinstance(node, exp.Anonymous):  # fonctions inconnues ex: IFNULL
            return "indirect"
        if isinstance(node, exp.If | exp.Case):
            return "indirect"
        node = node.parent

    return "direct"


def extract_accesses(sql: str, dialect: str = "mysql") -> list[dict]:
    """
    Retourne la liste de tous les accès champ/table avec leur type
    (direct / indirect) et l'alias exposé le cas échéant.
    """
    statement = sqlglot.parse_one(sql, dialect=dialect)

    if not isinstance(statement, exp.Select):
        raise ValueError("La requête fournie n'est pas un SELECT.")

    accesses: list[dict] = []
    seen: set[tuple] = set()  # dédoublonnage

    for select_expr in statement.selects:
        # Alias exposé dans le résultat
        if isinstance(select_expr, exp.Alias):
            exposed_as = select_expr.alias
            inner = select_expr.this
        else:
            exposed_as = None
            inner = select_expr

        # Toutes les colonnes dans cette expression SELECT
        for col in inner.find_all(exp.Column):
            if not col.table:
                continue  # on ignore les colonnes sans table explicite

            access_type = classify_column_in_expression(col, inner)

            key = (col.table, col.name, access_type, exposed_as)
            if key in seen:
                continue
            seen.add(key)

            accesses.append(
                {
                    "table": col.table,
                    "column": col.name,
                    "access": access_type,
                    "exposed_as": exposed_as if access_type == "direct" else None,
                }
            )

    return accesses


def build_lineage_tree(config: dict) -> dict:
    """Construit l'arbre de data lineage via sqlglot."""
    root = {"id": "root", "name": "root", "type": "root", "children": []}

    for file_name, functions in config.items():
        file_node = {"id": file_name, "name": file_name, "type": "file", "children": []}

        for func_name, func_def in functions.items():
            func_node = {
                "id": f"function.{func_name}",
                "name": func_name,
                "type": "function",
                "children": [],
            }

            sql = func_def.get("request", "")
            allowed_roles = func_def.get("allowedRolesRequester", [])

            try:
                accesses = extract_accesses(sql)
            except Exception as e:
                print(f"⚠️  [{file_name}.{func_name}] : {e}")
                accesses = []

            # Regroupement par table
            tables: dict[str, list[dict]] = {}
            for a in accesses:
                tables.setdefault(a["table"], []).append(a)

            for table_name, field_accesses in tables.items():
                table_node = {
                    "id": f"table.{table_name}",
                    "name": table_name,
                    "type": "table",
                    "children": [],
                }

                for access in field_accesses:
                    col_name = access["column"]
                    access_type = access["access"]
                    exposed_as = access["exposed_as"]

                    field_node = {
                        "id": f"field.{table_name}.{col_name}",
                        "name": col_name,
                        "type": "field",
                        "access": access_type,  # "direct" | "indirect"
                        "exposed_as": exposed_as,  # alias retourné, None si indirect
                        "children": [],
                    }

                    for role in allowed_roles:
                        role_node = {
                            "id": f"role.{role}",
                            "name": role,
                            "type": "role",
                            "children": [],
                        }
                        field_node["children"].append(role_node)

                    table_node["children"].append(field_node)

                func_node["children"].append(table_node)

            file_node["children"].append(func_node)

        root["children"].append(file_node)

    return root
