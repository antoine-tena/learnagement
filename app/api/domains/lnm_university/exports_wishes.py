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
    "/university/admin/wishes/export",
    tags=["admin", "mobility"],
    summary="Export student mobility wishes to Excel",
    response_model=None,
)
def export_admin_wishes(current_user: Annotated[User, Depends(get_current_active_user)]) -> object:
    sql_request = SQLRequest(
        request="""
            SELECT
                e.id_etudiant AS ID_Etudiant,
                e.nom AS Nom,
                e.prenom AS Prenom,
                e.mail AS Email,
                f.nom_filiere AS Filiere,
                s.nom_statut AS Statut,
                IFNULL(e.mobility_note, 'N/A') AS Note,
                w.priority AS Priorite,
                u.name AS Universite_Partenaire,
                u.country AS Pays,
                sem.semestre AS Semestre_Demande,
                w.submission_date AS Date_Soumission
            FROM MOB_wishes w
            JOIN LNM_etudiant e ON e.id_etudiant = w.id_etudiant
            JOIN LNM_promo p ON p.id_promo = e.id_promo
            JOIN LNM_filiere f ON f.id_filiere = p.id_filiere
            JOIN LNM_statut s ON s.id_statut = p.id_statut
            JOIN MOB_partner_university u ON u.id_partner_university = w.id_partner_university
            JOIN LNM_semestre sem ON sem.id_semestre = w.id_semestre
            WHERE p.annee = 4
            ORDER BY e.nom ASC, e.prenom ASC, w.priority ASC
        """,
        params=None,
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Voeux Etudiants"

    headers = [
        "ID Etudiant",
        "Nom",
        "Prénom",
        "Email",
        "Filière",
        "Statut",
        "Note de Mobilité",
        "Priorité",
        "Université Partenaire",
        "Pays",
        "Semestre Demandé",
        "Date de Soumission",
    ]
    ws.append(headers)

    for row in result:
        ws.append(
            [
                row.get("ID_Etudiant", ""),
                row.get("Nom", ""),
                row.get("Prenom", ""),
                row.get("Email", ""),
                row.get("Filiere", ""),
                row.get("Statut", ""),
                row.get("Note", ""),
                row.get("Priorite", ""),
                row.get("Universite_Partenaire", ""),
                row.get("Pays", ""),
                row.get("Semestre_Demande", ""),
                str(row.get("Date_Soumission", "")) if row.get("Date_Soumission") else "Non Soumis",
            ]
        )

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = export_filename("Voeux_Mobilite")
    headers_dict = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_dict,
    )


@router.get(
    "/university/admin/assignments/export",
    tags=["admin", "mobility"],
    summary="Export student mobility assignments to Excel",
    response_model=None,
)
def export_admin_assignments(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    sql_request = SQLRequest(
        request="""
            SELECT
                e.id_etudiant AS ID_Etudiant,
                e.nom AS Nom,
                e.prenom AS Prenom,
                e.mail AS Email,
                f.nom_filiere AS Filiere,
                s.nom_statut AS Statut,
                IFNULL(e.mobility_note, 'N/A') AS Note,
                IFNULL(e.mobility_z_score, 'N/A') AS Moyenne_Centree_Reduite,
                CASE
                    WHEN u.name IS NOT NULL THEN u.name
                    WHEN (SELECT COUNT(*) FROM MOB_wishes w
                        WHERE w.id_etudiant = e.id_etudiant) = 0 THEN 'Aucun vœu'
                    ELSE 'Non affecté'
                END AS Universite_Affectee,
                IFNULL((
                    SELECT mw.priority
                    FROM MOB_wishes mw
                    WHERE mw.id_etudiant = e.id_etudiant
                      AND mw.id_partner_university = a.id_partner_university
                    LIMIT 1
                ), 'N/A') AS Ordre_Voeu,
                IFNULL(u.country, 'N/A') AS Pays,
                IFNULL(sem.semestre, 'N/A') AS Semestre_Affecte,
                CASE
                    WHEN a.status IS NOT NULL THEN a.status
                    WHEN (SELECT COUNT(*) FROM MOB_wishes w
                        WHERE w.id_etudiant = e.id_etudiant) = 0 THEN 'Retardataire'
                    ELSE 'Non affecté'
                END AS Statut_Affectation
            FROM LNM_etudiant e
            JOIN LNM_promo p ON p.id_promo = e.id_promo
            JOIN LNM_filiere f ON f.id_filiere = p.id_filiere
            JOIN LNM_statut s ON s.id_statut = p.id_statut

            LEFT JOIN MOB_assignment a ON a.id_etudiant = e.id_etudiant
            LEFT JOIN MOB_partner_university u ON u.id_partner_university = a.id_partner_university
            LEFT JOIN LNM_semestre sem ON sem.id_semestre = a.id_semestre
            WHERE p.annee = 4
            ORDER BY e.nom ASC, e.prenom ASC
        """,
        params=None,
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Affectations Etudiants"

    headers = [
        "ID Etudiant",
        "Nom",
        "Prénom",
        "Email",
        "Filière",
        "Statut",
        "Note de Mobilité",
        "Moyenne Centrée Réduite",
        "Université Affectée",
        "Pays",
        "Semestre Affecté",
        "Statut de l'affectation",
    ]
    ws.append(headers)

    for row in result:
        ws.append(
            [
                row.get("ID_Etudiant", ""),
                row.get("Nom", ""),
                row.get("Prenom", ""),
                row.get("Email", ""),
                row.get("Filiere", ""),
                row.get("Statut", ""),
                row.get("Note", ""),
                row.get("Moyenne_Centree_Reduite", ""),
                row.get("Universite_Affectee", ""),
                row.get("Pays", ""),
                row.get("Semestre_Affecte", ""),
                row.get("Statut_Affectation", ""),
            ]
        )

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = export_filename("Affectations_Mobilite")
    headers_dict = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_dict,
    )
