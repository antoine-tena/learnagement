import io
from typing import Annotated

import openpyxl
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.dependencies import get_current_active_user
from core.clock import export_filename
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/university/admin/mobility/diagnostics/export/{category}",
    tags=["admin", "mobility"],
    summary="Export specific diagnostic category to Excel",
    response_model=None,
)
def export_mobility_diagnostics(
    category: str, current_user: Annotated[User, Depends(get_current_active_user)]
) -> object:
    sql_request = SQLRequest(
        request="""
            SELECT
                e.id_etudiant,
                e.nom,
                e.prenom,
                e.mail,
                f.nom_filiere,
                s.nom_statut,
                e.mobility_note,
                e.mobility_completed,
                (SELECT COUNT(w.id_partner_university) FROM MOB_wishes w
                    WHERE w.id_etudiant = e.id_etudiant) as wish_count,
                (SELECT MAX(w.submission_date) FROM MOB_wishes w
                    WHERE w.id_etudiant = e.id_etudiant) as last_submission_date
            FROM LNM_etudiant e
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
            JOIN LNM_statut s ON p.id_statut = s.id_statut
            WHERE p.annee = 4
            ORDER BY e.nom ASC, e.prenom ASC
        """,
        params=None,
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)

    filtered_students = []

    if result:
        for row in result:
            wish_count = row.get("wish_count", 0)
            last_sub = row.get("last_submission_date")
            is_completed = row.get("mobility_completed") == 1

            last_sub_str = str(last_sub).strip().lower() if last_sub is not None else ""
            is_submitted = last_sub_str and last_sub_str not in [
                "none",
                "null",
                "0000-00-00 00:00:00",
                "0000-00-00",
                "0",
            ]

            match = False
            if (
                (category == "validated" and is_completed)
                or (category == "remaining" and not is_completed)
                or (category == "submitted" and wish_count > 0 and is_submitted)
                or (category == "in_progress" and wish_count > 0 and not is_submitted)
                or (category == "retardataires" and wish_count == 0)
            ):
                match = True

            if match:
                filtered_students.append(row)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Export {category.capitalize()}"

    headers = [
        "ID Etudiant",
        "Nom",
        "Prénom",
        "Email",
        "Filière",
        "Statut Etudiant",
        "Note de Mobilité",
    ]
    if category not in ["retardataires", "validated"]:
        headers.append("Nombre de vœux enregistrés")

    ws.append(headers)

    for student in filtered_students:
        row_data = [
            student.get("id_etudiant", ""),
            student.get("nom", ""),
            student.get("prenom", ""),
            student.get("mail", ""),
            student.get("nom_filiere", ""),
            student.get("nom_statut", ""),
            student.get("mobility_note", ""),
        ]
        if category not in ["retardataires", "validated"]:
            row_data.append(student.get("wish_count", 0))

        ws.append(row_data)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = export_filename(category)
    headers_dict = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_dict,
    )
