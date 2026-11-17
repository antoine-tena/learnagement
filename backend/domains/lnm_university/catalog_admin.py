from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Connection

from api.dependencies import get_current_active_user
from db.connection import get_connection
from models.request import SQLRequest
from models.user import User

from ._db import db_request
from .schemas import UniversityAdminPayload, UniversityPlacePayload

router = APIRouter()


def _sync_university_places(
    current_user: User,
    id_partner_university: int,
    places: list[UniversityPlacePayload],
    conn: Connection,
) -> None:
    normalized_places: dict[tuple[int, int], int] = {}
    for place in places:
        if place.number_of_places <= 0:
            continue
        normalized_places[(place.id_filiere, place.annee)] = int(place.number_of_places)

    resolved_places: list[dict[str, int]] = []
    for (id_filiere, annee), number_of_places in normalized_places.items():
        resolved_places.append(
            {
                "id_filiere": id_filiere,
                "annee": annee,
                "number_of_places": number_of_places,
            }
        )

    delete_places_request = {
        "request": """
                        DELETE FROM MOB_partner_university_places
                        WHERE id_partner_university = %(id_partner_university)s
                    """,
        "params": {
            "id_partner_university": id_partner_university,
        },
        "allowedRolesRequester": ["relations_internationales"],
    }
    db_request(current_user, SQLRequest(**delete_places_request), conn=conn)

    for place in resolved_places:
        insert_place_request = {
            "request": """
                            INSERT INTO MOB_partner_university_places (id_partner_university,
                                id_filiere, annee, number_of_places)
                            VALUES (%(id_partner_university)s, %(id_filiere)s, %(annee)s,
                                %(number_of_places)s)
                        """,
            "params": {
                "id_partner_university": id_partner_university,
                "id_filiere": place["id_filiere"],
                "annee": place["annee"],
                "number_of_places": place["number_of_places"],
            },
            "allowedRolesRequester": ["relations_internationales"],
        }
        db_request(current_user, SQLRequest(**insert_place_request), conn=conn)


@router.post(
    "/university/admin",
    tags=["mobility"],
    summary="Create partner university for RI",
    description=(
        "Create a partner university and its places by filiere/semester for International "
        "Relations admins"
    ),
    response_model=None,
)
def create_university_ri(
    payload: UniversityAdminPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    name = payload.name.strip()
    country = payload.country.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Le nom de l'universite est obligatoire.")
    if not country:
        raise HTTPException(status_code=400, detail="Le pays est obligatoire.")

    insert_request = {
        "request": """
                        INSERT INTO MOB_partner_university (
                            name, code, country, address, latitude, longitude, website,
                            languages, note_min, type, S8_total_places, S9_total_places
                        ) VALUES (
                            %(name)s, %(code)s, %(country)s, %(address)s, %(latitude)s,
                            %(longitude)s, %(website)s, %(languages)s, %(note_min)s, %(type)s,
                            %(S8_total_places)s, %(S9_total_places)s
                        )
                    """,
        "params": {
            "name": name,
            "code": payload.code,
            "country": country,
            "address": payload.address,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "website": payload.website,
            "languages": payload.languages,
            "note_min": payload.note_min,
            "type": payload.type,
            "S8_total_places": payload.S8_total_places,
            "S9_total_places": payload.S9_total_places,
        },
        "allowedRolesRequester": ["relations_internationales"],
    }

    try:
        with get_connection() as conn:
            db_request(current_user, SQLRequest(**insert_request), conn=conn)
            rows = db_request(
                current_user,
                SQLRequest(
                    request="SELECT LAST_INSERT_ID() AS id_partner_university",
                    allowedRolesRequester=["relations_internationales"],
                ),
                conn=conn,
            )
            id_partner_university = int(rows[0]["id_partner_university"])
            _sync_university_places(current_user, id_partner_university, payload.places, conn)
    except HTTPException as exc:
        if exc.status_code == 403:
            raise
        raise HTTPException(status_code=400, detail=f"Creation impossible: {exc.detail}") from exc

    return {
        "message": "Universite creee.",
        "id_partner_university": id_partner_university,
    }


@router.put(
    "/university/admin/{id_partner_university:int}",
    tags=["mobility"],
    summary="Update partner university for RI",
    description=(
        "Update a partner university and its places by filiere/semester for International "
        "Relations admins"
    ),
    response_model=None,
)
def update_university_ri(
    id_partner_university: int,
    payload: UniversityAdminPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    allowed = ["relations_internationales"]

    exists_request = {
        "request": """
                        SELECT id_partner_university
                        FROM MOB_partner_university
                        WHERE id_partner_university = %(id_partner_university)s
                    """,
        "params": {
            "id_partner_university": id_partner_university,
        },
        "allowedRolesRequester": allowed,
    }
    rows = db_request(current_user, SQLRequest(**exists_request))
    if not rows:
        raise HTTPException(status_code=404, detail="Universite introuvable.")

    name = payload.name.strip()
    country = payload.country.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Le nom de l'universite est obligatoire.")
    if not country:
        raise HTTPException(status_code=400, detail="Le pays est obligatoire.")

    update_request = {
        "request": """
                        UPDATE MOB_partner_university
                        SET
                            name = %(name)s,
                            code = %(code)s,
                            country = %(country)s,
                            address = %(address)s,
                            latitude = %(latitude)s,
                            longitude = %(longitude)s,
                            website = %(website)s,
                            languages = %(languages)s,
                            note_min = %(note_min)s,
                            type = %(type)s,
                            S8_total_places = %(S8_total_places)s,
                            S9_total_places = %(S9_total_places)s
                        WHERE id_partner_university = %(id_partner_university)s
                    """,
        "params": {
            "id_partner_university": id_partner_university,
            "name": name,
            "code": payload.code,
            "country": country,
            "address": payload.address,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "website": payload.website,
            "languages": payload.languages,
            "note_min": payload.note_min,
            "type": payload.type,
            "S8_total_places": payload.S8_total_places,
            "S9_total_places": payload.S9_total_places,
        },
        "allowedRolesRequester": allowed,
    }

    try:
        with get_connection() as conn:
            db_request(current_user, SQLRequest(**update_request), conn=conn)
            _sync_university_places(current_user, id_partner_university, payload.places, conn)
    except HTTPException as exc:
        if exc.status_code == 403:
            raise
        raise HTTPException(
            status_code=400, detail=f"Mise a jour impossible: {exc.detail}"
        ) from exc

    return {
        "message": "Universite mise a jour.",
        "id_partner_university": id_partner_university,
    }
