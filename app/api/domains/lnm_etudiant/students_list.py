from typing import Annotated, Self

from fastapi import APIRouter, Depends
from pydantic import BaseModel, model_validator

from api.dependencies import Rows, db_request, get_current_active_user
from models.request import SQLRequest
from models.user import User

router = APIRouter()


class AbsencesFilters(BaseModel):
    id_responsable: int | None = None
    id_enseignant: int | None = None

    @model_validator(mode="after")
    def check_exclusive(self) -> Self:
        if self.id_responsable is not None and self.id_enseignant is not None:
            raise ValueError("Fournissez soit id_responsable, soit id_enseignant, pas les deux")
        return self


@router.get(
    "/etudiants",
    tags=["student"],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiants(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                        SELECT
                            LNM_etudiant.`id_etudiant`,
                            LNM_etudiant.`nom`,
                            LNM_etudiant.`prenom`,
                            LNM_etudiant.`mail`,
                            ExplicitSecondaryKs_LNM_etudiant.ExplicitSecondaryK,
                            ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK as 'promo'
                        FROM LNM_etudiant
                        JOIN ExplicitSecondaryKs_LNM_etudiant
                            ON ExplicitSecondaryKs_LNM_etudiant.id_etudiant
                                = LNM_etudiant.id_etudiant
                        LEFT JOIN ExplicitSecondaryKs_LNM_promo
                            ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_etudiant.id_promo
                        ORDER BY ExplicitSecondaryK;
                    """,
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/absences",
    tags=["student", "administratif"],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiants_absences(
    current_user: Annotated[User, Depends(get_current_active_user)],
    filters: Annotated[AbsencesFilters, Depends()],
) -> Rows:
    request = {
        "request": """SELECT ExplicitSecondaryKs_LNM_etudiant.ExplicitSecondaryK as etudiant,
                              ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK as promo,
                              MAQUETTE_module.code_module,
                              DATE_FORMAT(CLASS_session.schedule, '%Y-%m-%dT%H:%i') AS schedule
                       FROM `CLASS_absence`
                                JOIN CLASS_session
                                    ON CLASS_session.id_session = CLASS_absence.id_session
                                JOIN MAQUETTE_module_sequence
                                    ON MAQUETTE_module_sequence.id_module_sequence
                                        = CLASS_session.id_module_sequence
                                JOIN MAQUETTE_module_sequencage
                                    ON MAQUETTE_module_sequencage.id_module_sequencage
                                        = MAQUETTE_module_sequence.id_module_sequencage
                                JOIN MAQUETTE_module
                                    ON MAQUETTE_module.id_module
                                        = MAQUETTE_module_sequencage.id_module
                                JOIN LNM_etudiant
                                    ON LNM_etudiant.id_etudiant = CLASS_absence.id_etudiant
                                JOIN LNM_promo ON LNM_promo.id_promo = LNM_etudiant.id_promo
                                JOIN LNM_filiere ON LNM_filiere.id_filiere = LNM_promo.id_filiere
                                JOIN LNM_statut ON LNM_statut.id_statut = LNM_promo.id_statut
                                JOIN ExplicitSecondaryKs_LNM_etudiant
                                    ON ExplicitSecondaryKs_LNM_etudiant.id_etudiant
                                        = LNM_etudiant.id_etudiant
                                JOIN ExplicitSecondaryKs_LNM_promo
                                    ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_promo.id_promo
                    """,
        "allowedRolesRequester": {
            "roles": ["responsable_etudes"],
        },
    }

    # if id_responsable filter is set
    if current_user.mmain_role == "enseignant" and filters.id_responsable is not None:
        request["request"] += """ WHERE MAQUETTE_module.id_responsable = %(id_responsable)s"""
        request["params"] = {
            "id_responsable": filters.id_responsable,
        }
        request["allowedRolesRequester"]["owner"] = {"role": "enseignant", "id": "id_responsable"}

    # if id_enseignant filter is set
    elif current_user.mmain_role == "enseignant" and filters.id_enseignant is not None:
        request["request"] += """ WHERE CLASS_session.id_enseignant = %(id_enseignant)s"""
        request["params"] = {
            "id_enseignant": filters.id_enseignant,
        }
        request["allowedRolesRequester"]["owner"] = {"role": "enseignant", "id": "id_enseignant"}

    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/{id_etudiant:int}",
    tags=["student"],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                        SELECT
                            LNM_etudiant.`id_etudiant`,
                            LNM_etudiant.`nom`,
                            LNM_etudiant.`prenom`,
                            LNM_etudiant.`mail`,
                            LNM_etudiant.`password_updated`,
                            ExplicitSecondaryK,
                            LNM_filiere.nom_filiere,
                            LNM_statut.nom_statut
                        FROM LNM_etudiant
                                 JOIN ExplicitSecondaryKs_LNM_etudiant
                                     ON ExplicitSecondaryKs_LNM_etudiant.id_etudiant
                                         = LNM_etudiant.id_etudiant
                                 JOIN LNM_promo ON LNM_promo.id_promo = LNM_etudiant.id_promo
                                 JOIN LNM_filiere ON LNM_filiere.id_filiere = LNM_promo.id_filiere
                                 JOIN LNM_statut ON LNM_statut.id_statut=LNM_promo.id_statut
                        WHERE LNM_etudiant.id_etudiant = %(id_etudiant)s;
                    """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": [],
        },
        "owner": {"role": "etudiant", "id": "id_etudiant"},
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/{id_etudiant:int}/absences",
    tags=[
        "administratif",
        "student",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant_absences(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """SELECT MAQUETTE_module.code_module,
                              DATE_FORMAT(CLASS_session.schedule, '%Y-%m-%dT%H:%i') AS schedule
                       FROM `CLASS_absence`
                                JOIN CLASS_session
                                    ON CLASS_session.id_session = CLASS_absence.id_session
                                JOIN MAQUETTE_module_sequence
                                    ON MAQUETTE_module_sequence.id_module_sequence
                                        = CLASS_session.id_module_sequence
                                JOIN MAQUETTE_module_sequencage
                                    ON MAQUETTE_module_sequencage.id_module_sequencage
                                        = MAQUETTE_module_sequence.id_module_sequencage
                                JOIN MAQUETTE_module
                                    ON MAQUETTE_module.id_module
                                        = MAQUETTE_module_sequencage.id_module
                                JOIN LNM_etudiant
                                    ON LNM_etudiant.id_etudiant = CLASS_absence.id_etudiant
                       WHERE LNM_etudiant.`id_etudiant` = %(id_etudiant)s
        """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": ["responsable_etudes"],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))
