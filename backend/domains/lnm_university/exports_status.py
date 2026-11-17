import io
from datetime import datetime
from typing import Annotated

import openpyxl
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.dependencies import get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/university/admin/mobility/assigned-students/export/{status}",
    tags=["admin", "mobility"],
    summary="Export assigned students by status",
    response_model=None,
)
def export_assigned_students_status(
    status: str, current_user: Annotated[User, Depends(get_current_active_user)]
) -> object:
    if status not in ["accepted", "pending", "declined"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    sql_request = SQLRequest(
        request="""
            SELECT a.id_etudiant, a.status, e.nom, e.prenom, e.mail, e.mobility_z_score,
                   f.nom_filiere, s.nom_statut, u.name as university_name, u.country
            FROM MOB_assignment a
            JOIN LNM_etudiant e ON e.id_etudiant = a.id_etudiant
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
            JOIN LNM_statut s ON p.id_statut = s.id_statut
            JOIN MOB_partner_university u ON a.id_partner_university = u.id_partner_university
            WHERE p.annee = 4 AND a.status = %(status)s
            ORDER BY e.nom ASC, e.prenom ASC
        """,
        params={"status": status},
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Affectations {status.capitalize()}"

    headers = [
        "ID Etudiant",
        "Nom",
        "Prénom",
        "Email",
        "Filière",
        "Statut Etudiant",
        "Moyenne Centrée Réduite",
        "Université Attribuée",
        "Pays",
        "Statut Affectation",
    ]
    ws.append(headers)

    if result:
        for row in result:
            ws.append(
                [
                    row.get("id_etudiant", ""),
                    row.get("nom", ""),
                    row.get("prenom", ""),
                    row.get("mail", ""),
                    row.get("nom_filiere", ""),
                    row.get("nom_statut", ""),
                    row.get("mobility_z_score", ""),
                    row.get("university_name", ""),
                    row.get("country", ""),
                    row.get("status", ""),
                ]
            )

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"Export_Affectations_{status}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    headers_res = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_res,
    )


@router.get(
    "/university/admin/mobility/unassigned-students/export",
    tags=["admin", "mobility"],
    summary="Export students with submitted wishes but no assignments",
    response_model=None,
)
def export_unassigned_students(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    sql_request = SQLRequest(
        request="""
            SELECT DISTINCT e.id_etudiant, e.nom, e.prenom, e.mail, e.mobility_z_score,
                   f.nom_filiere, s.nom_statut
            FROM MOB_wishes w
            JOIN LNM_etudiant e ON w.id_etudiant = e.id_etudiant
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
            JOIN LNM_statut s ON p.id_statut = s.id_statut
            LEFT JOIN MOB_assignment a ON e.id_etudiant = a.id_etudiant
            WHERE p.annee = 4
              AND w.submission_date IS NOT NULL
              AND a.id_etudiant IS NULL
            ORDER BY e.nom ASC, e.prenom ASC
        """,
        params={},
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Non Affectes"

    headers = [
        "ID Etudiant",
        "Nom",
        "Prénom",
        "Email",
        "Filière",
        "Statut Etudiant",
        "Moyenne Centrée Réduite",
        "Statut Affectation",
    ]
    ws.append(headers)

    if result:
        for row in result:
            ws.append(
                [
                    row.get("id_etudiant", ""),
                    row.get("nom", ""),
                    row.get("prenom", ""),
                    row.get("mail", ""),
                    row.get("nom_filiere", ""),
                    row.get("nom_statut", ""),
                    row.get("mobility_z_score", ""),
                    "Non Affecté",
                ]
            )

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"Export_Non_Affectes_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    headers_res = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_res,
    )
