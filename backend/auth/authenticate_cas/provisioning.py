"""Détermination de rôle/promo et provisionnement en base des utilisateurs CAS."""

import json
import os

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from api.dependencies import logger
from models.user import UserInDB

from .schemas import CasUserProvision


def _determine_role_from_cas_groups(members: list[str]) -> str | None:
    """
    Détermine le rôle principal depuis les groupes CAS.
    Les groupes dans .env sont des CN (ex: "enseignants").
    """
    member_cns = set()
    for dn in members:
        parts = dn.split(",")
        if parts and parts[0].startswith("cn="):
            member_cns.add(parts[0][3:])

    def groups_from_env(key: str) -> set[str]:
        val = os.getenv(key, "").strip()
        return set(val.split()) if val else set()

    main_role = None

    if member_cns & groups_from_env("CAS_ALLOWED_GROUPS_4_ADMINISTRATIF"):
        main_role = "administratif"
    elif member_cns & groups_from_env("CAS_ALLOWED_GROUPS_4_ENSEIGNANT"):
        main_role = "enseignant"
    elif member_cns & groups_from_env("CAS_ALLOWED_GROUPS_4_ETUDIANT"):
        main_role = "etudiant"

    return main_role


def _determine_promo_from_cas_groups(members: list[str]) -> int | None:
    """
    Détermine l'id_promo d'un étudiant depuis ses groupes CAS
    en croisant avec CAS_ETUDIANTS_2_PROMO du .env.

    CAS_ETUDIANTS_2_PROMO est un JSON :
    [{"groupe": "idu4-fise", "promo": "IDU FISE 4 Annecy"}, ...]
    """
    import auth.authenticate_cas as pkg

    member_cns = set()
    for dn in members:
        parts = dn.split(",")
        if parts and parts[0].startswith("cn="):
            member_cns.add(parts[0][3:])

    raw = os.getenv("CAS_ETUDIANTS_2_PROMO", "[]")
    try:
        mapping = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"CAS_ETUDIANTS_2_PROMO mal formé dans .env {e}")
        return None

    promo_name = next(
        (entry["promo"] for entry in mapping if entry["groupe"] in member_cns),
        None,
    )
    if promo_name is None:
        logger.warning(f"Aucun groupe étudiant connu parmi : {member_cns}")
        return None

    try:
        with pkg.get_connection() as conn:
            return conn.execute(
                text("""
                SELECT LNM_promo.id_promo
                FROM LNM_promo
                JOIN ExplicitSecondaryKs_LNM_promo
                  ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_promo.id_promo
                WHERE ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK = :promo_name
            """),
                {"promo_name": promo_name},
            ).scalar()
    except Exception as e:
        logger.error(f"DB error lors de la résolution de promo '{promo_name}': {e}")
        return None


def _create_cas_user(data: CasUserProvision, main_role: str) -> UserInDB | None:
    import auth.authenticate_cas as pkg

    params: dict[str, object] = {
        "prenom": data.prenom,
        "nom": data.nom,
        "mail": data.email,
        "login": data.login,
    }

    if main_role == "enseignant":
        sql = """
            INSERT INTO LNM_enseignant
                (prenom, nom, mail, login, intern_account, password)
            VALUES (:prenom, :nom, :mail, :login, 0, NULL)
        """
    elif main_role == "administratif":
        sql = """
            INSERT INTO LNM_administratif
                (nom, prenom, mail, login, intern_account, password)
            VALUES (:nom, :prenom, :mail, :login, 0, NULL)
        """
    elif main_role == "etudiant":
        id_promo = _determine_promo_from_cas_groups(data.members)
        if id_promo is None:
            logger.error(f"Aucune promo trouvée pour '{data.login}' : {data.members}")
            return None
        params["id_promo"] = id_promo
        sql = """
            INSERT INTO LNM_etudiant
                (nom, prenom, mail, login, intern_account, password, id_promo)
            VALUES (:nom, :prenom, :mail, :login, 0, NULL, :id_promo)
        """
    else:
        logger.error(f"Rôle inconnu '{main_role}' pour '{data.login}'")
        return None

    try:
        with pkg.get_connection() as conn:
            conn.execute(text(sql), params)
    except IntegrityError:
        logger.warning(f"Utilisateur '{data.login}' déjà provisionné (accès concurrent)")
    except Exception as e:
        logger.error(f"DB error during CAS provisioning: {e}")
        return None

    return pkg.get_user(data.login)
