"""Construction de l'arbre simple des droits d'accès par expression régulière."""

import inspect
import re


def parse_select_fields(sql: str) -> list[dict]:
    """Extrait les champs d'un SELECT sous forme {table, field}."""
    match = re.search(r"SELECT\s+(.*?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return []

    raw_fields = match.group(1).split(",")
    fields = []

    for raw in raw_fields:
        raw = raw.strip()
        if "." in raw:
            table, field = raw.split(".", 1)
            fields.append({"table": table.strip(), "field": field.strip()})
        else:
            fields.append({"table": "_unknown", "field": raw})

    return fields


def build_tree(config: dict) -> dict:
    """Construit l'arbre de droits d'accès depuis la config JSON."""
    root = {"id": "root", "name": "root", "type": "root", "children": []}

    for file_name, functions in config.items():
        # Niveau 1 — fichier
        file_node = {"id": file_name, "name": file_name, "type": "file", "children": []}

        for func_name, func_def in functions.items():
            # Niveau 2 — fonction
            func_node = {
                "id": f"{file_name}.{func_name}",
                "name": func_name,
                "type": "function",
                "children": [],
            }

            sql = func_def.get("request", "")
            allowed_roles = func_def.get("allowedRolesRequester", [])
            fields = parse_select_fields(sql)

            # Regroupement des champs par table
            tables: dict[str, list[str]] = {}
            for f in fields:
                tables.setdefault(f["table"], []).append(f["field"])

            for table_name, field_list in tables.items():
                # Niveau 3 — table
                table_node = {
                    "id": f"{file_name}.{func_name}.{table_name}",
                    "name": table_name,
                    "type": "table",
                    "children": [],
                }

                for field_name in field_list:
                    # Niveau 4 — champ
                    field_node = {
                        "id": f"{file_name}.{func_name}.{table_name}.{field_name}",
                        "name": field_name,
                        "type": "field",
                        "children": [],
                    }
                    if callable(allowed_roles):
                        source = inspect.getsource(allowed_roles).strip()
                        name = "".join(source.split(":")[1:]).strip()
                        role_id = "".join(name.split("[")[0]).strip()
                        # Niveau 5 — lambda rôle
                        role_node = {
                            "id": f"{file_name}.{func_name}.{table_name}.{field_name}.{role_id}",
                            "name": name,
                            "type": "role",
                            "children": [],
                        }
                        field_node["children"].append(role_node)
                    else:
                        for role in allowed_roles:
                            # Niveau 5 — static rôle
                            role_node = {
                                "id": f"{file_name}.{func_name}.{table_name}.{field_name}.{role}",
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
