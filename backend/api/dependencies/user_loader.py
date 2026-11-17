"""Chargement des utilisateurs et de leurs responsabilités depuis la base de données."""

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from core.logging import logger
from db.connection import get_read_connection
from models.user import UserInDB


def load_enseignant_responsibilities(rows: list[dict]) -> list[dict]:
    """
    Transforme les lignes SQL à plat en liste de responsabilités avec
    leurs dimensions sous forme de dict.
    """
    resp_map = {}
    for row in rows:
        rid = row["id_enseignant_responsabilites"]
        if rid not in resp_map:
            resp_map[rid] = {
                "type_objet": row["type_objet"],
                "dimensions": {},  # { "filiere": "IDU", "niveau": "FI4", ... }
            }
        if row["dimension"]:  # LEFT JOIN → peut être NULL si aucune dimension
            resp_map[rid]["dimensions"][row["dimension"]] = row["valeur"]

    return list(resp_map.values())


def _fetch_administratif(conn: Connection, user_login: str) -> UserInDB | None:
    row = (
        conn.execute(
            text("""
        SELECT LNM_administratif.id_administratif AS id,
               LNM_administratif.*,
               ExplicitSecondaryKs_LNM_administratif.ExplicitSecondaryK
        FROM LNM_administratif
        JOIN ExplicitSecondaryKs_LNM_administratif
          ON ExplicitSecondaryKs_LNM_administratif.id_administratif
              = LNM_administratif.id_administratif
        WHERE login = :login
    """),
            {"login": user_login},
        )
        .mappings()
        .first()
    )

    if row is None:
        return None

    user_dict = dict(row)  # RowMapping est immuable : on copie
    if user_dict.get("intern_account") != 0 and not user_dict.get("password"):
        logger.warning(f"Inactive user '{user_login}' try to connect")
        return None

    user_dict["main_role"] = "administratif"
    user_dict["roles"] = ["connected_user", "administratif", user_dict["ExplicitSecondaryK"]]

    roles = (
        conn.execute(
            text("""
        SELECT LNM_role.role
        FROM LNM_administratif
        JOIN LNM_administratif_as_role
          ON LNM_administratif_as_role.id_administratif = LNM_administratif.id_administratif
        JOIN LNM_role ON LNM_role.id_role = LNM_administratif_as_role.id_role
        WHERE login = :login
    """),
            {"login": user_login},
        )
        .scalars()
        .all()
    )
    user_dict["roles"] += roles

    return UserInDB(**user_dict)


def _fetch_enseignant(conn: Connection, user_login: str) -> UserInDB | None:
    row = (
        conn.execute(
            text("""
        SELECT LNM_enseignant.id_enseignant AS id,
               LNM_enseignant.*,
               ExplicitSecondaryKs_LNM_enseignant.ExplicitSecondaryK
        FROM LNM_enseignant
        JOIN ExplicitSecondaryKs_LNM_enseignant
          ON ExplicitSecondaryKs_LNM_enseignant.id_enseignant = LNM_enseignant.id_enseignant
        WHERE login = :login
    """),
            {"login": user_login},
        )
        .mappings()
        .first()
    )

    if row is None:
        return None

    user_dict = dict(row)
    if user_dict.get("intern_account") != 0 and not user_dict.get("password"):
        logger.warning(f"Inactive user '{user_login}' try to connect")
        return None

    user_dict["main_role"] = "enseignant"
    user_dict["roles"] = ["connected_user", "enseignant", user_dict["ExplicitSecondaryK"]]

    roles = (
        conn.execute(
            text("""
        SELECT LNM_role.role
        FROM LNM_enseignant
        JOIN LNM_enseignant_as_role
          ON LNM_enseignant_as_role.id_enseignant = LNM_enseignant.id_enseignant
        JOIN LNM_role ON LNM_role.id_role = LNM_enseignant_as_role.id_role
        WHERE login = :login
    """),
            {"login": user_login},
        )
        .scalars()
        .all()
    )
    user_dict["roles"] += roles

    responsibilities = (
        conn.execute(
            text("""
        SELECT LNM_enseignant_responsabilites.id_enseignant_responsabilites,
               LNM_responsabilite.type_objet,
               LNM_enseignant_responsabilite_dimensions.dimension,
               LNM_enseignant_responsabilite_dimensions.valeur
        FROM LNM_responsabilite
        JOIN LNM_enseignant_responsabilites
          ON LNM_enseignant_responsabilites.id_responsabilite = LNM_responsabilite.id_responsabilite
        JOIN LNM_enseignant
          ON LNM_enseignant.id_enseignant = LNM_enseignant_responsabilites.id_enseignant
        LEFT JOIN LNM_enseignant_responsabilite_dimensions
          ON LNM_enseignant_responsabilite_dimensions.id_enseignant_responsabilites
              = LNM_enseignant_responsabilites.id_enseignant_responsabilites
        WHERE login = :login
    """),
            {"login": user_login},
        )
        .mappings()
        .all()
    )
    user_dict["responsibilities"] = load_enseignant_responsibilities(responsibilities)

    return UserInDB(**user_dict)


def _fetch_etudiant(conn: Connection, user_login: str) -> UserInDB | None:
    row = (
        conn.execute(
            text("""
        SELECT LNM_etudiant.id_etudiant AS id,
               LNM_etudiant.*,
               ExplicitSecondaryKs_LNM_etudiant.ExplicitSecondaryK
        FROM LNM_etudiant
        JOIN ExplicitSecondaryKs_LNM_etudiant
          ON ExplicitSecondaryKs_LNM_etudiant.id_etudiant = LNM_etudiant.id_etudiant
        WHERE login = :login
    """),
            {"login": user_login},
        )
        .mappings()
        .first()
    )

    if row is None:
        return None

    user_dict = dict(row)
    if user_dict.get("intern_account") != 0 and not user_dict.get("password"):
        logger.warning(f"Inactive user '{user_login}' try to connect")
        return None

    user_dict["main_role"] = "etudiant"
    user_dict["roles"] = ["connected_user", "etudiant", user_dict["ExplicitSecondaryK"]]

    return UserInDB(**user_dict)


def get_user(user_login: str) -> UserInDB | None:
    user = None
    fetchers = (_fetch_administratif, _fetch_enseignant, _fetch_etudiant)

    try:
        with get_read_connection() as conn:  # UNE connexion pour tous les fetchers
            for fetcher in fetchers:
                user = fetcher(conn, user_login)
                if user:
                    break
    except SQLAlchemyError as e:
        logger.exception(e)
        raise HTTPException(status_code=503, detail="Database unavailable") from e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Undefined Get User Error") from e

    if user is not None:
        logger.info(f"User {user_login} logged")
    else:
        logger.error(f"Loging error with login: {user_login}")

    return user
