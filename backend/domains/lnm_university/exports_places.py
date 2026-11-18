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
from .assignments import sync_db_remaining_places

router = APIRouter()


@router.get(
    "/university/admin/places/export",
    tags=["admin", "mobility"],
    summary="Export partner university places status to Excel",
    response_model=None,
)
def export_admin_places(current_user: Annotated[User, Depends(get_current_active_user)]) -> object:
    sync_db_remaining_places(current_user)

    # Requête pour récupérer les universités, leurs places globales (S8/S9) et le détail par
    # filière.
    sql_request = SQLRequest(
        request="""
            SELECT
                u.id_partner_university,
                u.name AS university_name,
                u.country,
                IFNULL(u.S8_total_places, 0) AS S8_total,
                IFNULL(u.S9_total_places, 0) AS S9_total,
                IFNULL(u.S8_total_places, 0) AS S8_restant,
                IFNULL(u.S9_total_places, 0) AS S9_restant,
                f.nom_filiere,
                pl.annee,
                pl.number_of_places AS filiere_total,
                pl.number_of_places AS filiere_restant
            FROM MOB_partner_university u
            LEFT JOIN MOB_partner_university_places pl
                ON u.id_partner_university = pl.id_partner_university
            LEFT JOIN LNM_filiere f ON pl.id_filiere = f.id_filiere
            WHERE u.type != 'stage'
            ORDER BY u.name ASC, f.nom_filiere ASC, pl.annee ASC
        """,
        params=None,
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)
    # Récupérer la liste des filières pour construire les colonnes
    filiere_req = SQLRequest(
        request="SELECT nom_filiere FROM LNM_filiere ORDER BY nom_filiere ASC",
        allowedRolesRequester=["relations_internationales"],
    )
    filieres_result = db_request(current_user, filiere_req)
    filieres = [f["nom_filiere"] for f in filieres_result] if filieres_result else []

    # Récupérer les affectations actives (acceptées ou en attente) pour calculer le vrai reste
    assign_req = SQLRequest(
        request="""
        SELECT a.id_partner_university, a.id_semestre, f.nom_filiere
        FROM MOB_assignment a
        JOIN LNM_etudiant e ON a.id_etudiant = e.id_etudiant
        JOIN LNM_promo p ON e.id_promo = p.id_promo
        JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
        WHERE a.status = 'accepted'
    """,
        allowedRolesRequester=["relations_internationales"],
    )
    assign_result = db_request(current_user, assign_req)

    taken_global = {}
    taken_filiere = {}
    if assign_result:
        for a in assign_result:
            u_id = a.get("id_partner_university")
            sem = a.get("id_semestre")
            f_nom = a.get("nom_filiere")

            taken_global[(u_id, sem)] = taken_global.get((u_id, sem), 0) + 1
            taken_filiere[(u_id, sem, f_nom)] = taken_filiere.get((u_id, sem, f_nom), 0) + 1

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Etat des Places"

    headers = [
        "Université",
        "Pays",
        "Total S8 Initial",
        "Total S8 Restant",
        "Total S9 Initial",
        "Total S9 Restant",
    ]

    for f in filieres:
        headers.append(f"S8 {f} Initial")
        headers.append(f"S8 {f} Restant")

    for f in filieres:
        headers.append(f"S9 {f} Initial")
        headers.append(f"S9 {f} Restant")

    ws.append(headers)

    if result:
        uni_map = {}
        for row in result:
            u_name = row.get("university_name", "")
            u_id = row.get("id_partner_university")

            if u_name not in uni_map:
                s8_tot = row.get("S8_total", 0)
                s9_tot = row.get("S9_total", 0)
                uni_map[u_name] = {
                    "pays": row.get("country", ""),
                    "S8_total": s8_tot,
                    "S9_total": s9_tot,
                    "S8_restant": max(0, s8_tot - taken_global.get((u_id, 8), 0)),
                    "S9_restant": max(0, s9_tot - taken_global.get((u_id, 9), 0)),
                    "filieres": {},
                }

            annee = row.get("annee")
            nom_filiere = row.get("nom_filiere")
            if annee and nom_filiere:
                sem_num = 8 if annee == 4 else (9 if annee == 5 else annee * 2)
                sem = f"S{sem_num}"
                key = f"{sem}_{nom_filiere}"
                fil_tot = row.get("filiere_total", 0)
                uni_map[u_name]["filieres"][key] = {
                    "total": fil_tot,
                    "restant": max(0, fil_tot - taken_filiere.get((u_id, sem_num, nom_filiere), 0)),
                }

        for u_name, data in uni_map.items():
            row_data = [
                u_name,
                data["pays"],
                data["S8_total"],
                data["S8_restant"],
                data["S9_total"],
                data["S9_restant"],
            ]

            for f in filieres:
                key_s8 = f"S8_{f}"
                if key_s8 in data["filieres"]:
                    row_data.append(data["filieres"][key_s8]["total"])
                    row_data.append(data["filieres"][key_s8]["restant"])
                else:
                    row_data.append("")
                    row_data.append("")

            for f in filieres:
                key_s9 = f"S9_{f}"
                if key_s9 in data["filieres"]:
                    row_data.append(data["filieres"][key_s9]["total"])
                    row_data.append(data["filieres"][key_s9]["restant"])
                else:
                    row_data.append("")
                    row_data.append("")

            ws.append(row_data)

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = export_filename("Etat_Places")
    headers_dict = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers_dict,
    )
