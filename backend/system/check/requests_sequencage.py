"""Requêtes SQL de comparaison maquette vs séquençage."""

SEQUENCAGE_REQUESTS = {
    "get_maquette_vs_sequencage": {
        "request": """
                        SELECT hMaquette.ExplicitSecondaryK,
                               hMaquette.code_module,
                               hMaquette.hCM - hSession.hCM AS hCM_maquette_vs_sequencage,
                            hMaquette.hTD - hSession.hTD AS hTD_maquette_vs_sequencage,
                            hMaquette.hTP - hSession.hTP AS hTP_maquette_vs_sequencage,
                            hMaquette.hProj - hSession.hProj AS hProj_maquette_vs_sequencage
                        FROM
                            (SELECT ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK,
                                   MAQUETTE_module.code_module,
                                   SUM(LNM_promo.nbGroupeCM * IFNULL(MAQUETTE_module.hCM,
                                       0)) AS hCM,
                                   SUM(LNM_promo.nbGroupeTD * IFNULL(MAQUETTE_module.hTD,
                                       0)) AS hTD,
                                   SUM(LNM_promo.nbGroupeTP * IFNULL(MAQUETTE_module.hTP,
                                       0)) AS hTP,
                                   SUM(LNM_promo.nbGroupeCM * IFNULL(MAQUETTE_module.hProj,
                                       0)) AS hProj
                            FROM `MAQUETTE_module`
                            JOIN MAQUETTE_module_as_learning_unit
                                ON MAQUETTE_module_as_learning_unit.id_module
                                    = MAQUETTE_module.id_module
                            JOIN MAQUETTE_learning_unit
                                ON MAQUETTE_learning_unit.id_learning_unit
                                    = MAQUETTE_module_as_learning_unit.id_learning_unit
                            JOIN LNM_promo ON LNM_promo.id_promo = MAQUETTE_learning_unit.id_promo
                            JOIN ExplicitSecondaryKs_LNM_promo
                                ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_promo.id_promo
                            GROUP BY ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK,
                                     MAQUETTE_module.code_module
                            ) AS hMaquette
                        LEFT JOIN
                            (SELECT ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK,
                                    MAQUETTE_module.code_module,
                                    LNM_seance_type.type,
                                    SUM(CASE
                                        WHEN type = 'CM' THEN MAQUETTE_module_sequencage.duree_h
                                        ELSE 0 END) AS hCM,
                                    SUM(CASE
                                        WHEN type = 'TD' THEN MAQUETTE_module_sequencage.duree_h
                                        ELSE 0 END) AS hTD,
                                    SUM(CASE
                                        WHEN type = 'TP' THEN MAQUETTE_module_sequencage.duree_h
                                        ELSE 0 END) AS hTP,
                                    SUM(CASE
                                        WHEN type = 'PROJ' THEN MAQUETTE_module_sequencage.duree_h
                                        ELSE 0 END) AS hPROJ
                            FROM `MAQUETTE_module`
                            JOIN MAQUETTE_module_as_learning_unit
                                ON MAQUETTE_module_as_learning_unit.id_module
                                    = MAQUETTE_module.id_module
                            JOIN MAQUETTE_learning_unit
                                ON MAQUETTE_learning_unit.id_learning_unit
                                    = MAQUETTE_module_as_learning_unit.id_learning_unit
                            JOIN LNM_promo ON LNM_promo.id_promo = MAQUETTE_learning_unit.id_promo
                            JOIN ExplicitSecondaryKs_LNM_promo
                                ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_promo.id_promo
                            JOIN MAQUETTE_module_sequencage
                                ON MAQUETTE_module_sequencage.id_module = MAQUETTE_module.id_module
                            JOIN MAQUETTE_module_sequence
                                ON MAQUETTE_module_sequence.id_module_sequencage
                                    = MAQUETTE_module_sequencage.id_module_sequencage
                            JOIN CLASS_session
                                ON CLASS_session.id_module_sequence
                                    = MAQUETTE_module_sequence.id_module_sequence
                            JOIN LNM_seance_type
                                ON LNM_seance_type.id_seance_type
                                    = MAQUETTE_module_sequencage.id_seance_type
                            GROUP BY ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK,
                                    MAQUETTE_module.code_module,
                                    LNM_seance_type.type
                            ) AS hSession
                        ON hMaquette.code_module = hSession.code_module
                            AND hMaquette.ExplicitSecondaryK = hSession.ExplicitSecondaryK
                    """,
        "allowedRolesRequester": ["administratif", "responsable_etudes"],
    },
    "get_maquette_vs_sequencage_by_idResp": {
        "request": """
                    SELECT DISTINCT
                        MAQUETTE_module.id_module,
                        MAQUETTE_module.code_module,
                        CONCAT(IFNULL(hCM,0) - IFNULL(hCMCequenced,0), " / ",
                            IFNULL(hCM,0))  AS 'CM_to_plan',
                        CONCAT(IFNULL(hTD,0)  - IFNULL(hTDCequenced,0), " / ",
                            IFNULL(hTD,0)) AS 'TD_to_plan',
                        CONCAT(IFNULL(hTP,0)  - IFNULL(hTPCequenced,0), " / ",
                            IFNULL(hTP,0)) AS 'TP_to_plan',
                        CONCAT(IFNULL(hPROJ,0)  - IFNULL(hPROJCequenced,0), " / ",
                            IFNULL(hPROJ,0)) AS 'Proj_to_plan'
                    FROM MAQUETTE_module
                    LEFT JOIN (
                        SELECT code_module, SUM(nombre * duree_h) as hCMCequenced
                        FROM MAQUETTE_module_sequencage
                        JOIN MAQUETTE_module
                            ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                        JOIN LNM_seance_type
                            ON LNM_seance_type.id_seance_type
                                = MAQUETTE_module_sequencage.id_seance_type
                        JOIN LNM_groupe_type
                            ON LNM_groupe_type.id_groupe_type
                                = MAQUETTE_module_sequencage.id_groupe_type
                        WHERE LNM_seance_type.type = 'CM' AND LNM_groupe_type.groupe_type = 'PROMO'
                            OR LNM_seance_type.type = 'Exam'
                            AND LNM_groupe_type.groupe_type = 'PROMO'
                        GROUP BY code_module) CMsequenced
                            ON  CMsequenced.code_module = MAQUETTE_module.code_module
                    LEFT JOIN (
                        SELECT code_module, SUM(nombre * duree_h) as hTDCequenced
                        FROM MAQUETTE_module_sequencage
                        JOIN MAQUETTE_module
                            ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                        JOIN LNM_seance_type
                            ON LNM_seance_type.id_seance_type
                                = MAQUETTE_module_sequencage.id_seance_type
                        JOIN LNM_groupe_type
                            ON LNM_groupe_type.id_groupe_type
                                = MAQUETTE_module_sequencage.id_groupe_type
                        WHERE LNM_seance_type.type = 'TD' AND LNM_groupe_type.groupe_type = 'TD'
                        GROUP BY code_module) TDsequenced
                            ON  TDsequenced.code_module = MAQUETTE_module.code_module
                    LEFT JOIN (
                        SELECT code_module, SUM(nombre * duree_h) as hTPCequenced
                        FROM MAQUETTE_module_sequencage
                        JOIN MAQUETTE_module
                            ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                        JOIN LNM_seance_type
                            ON LNM_seance_type.id_seance_type
                                = MAQUETTE_module_sequencage.id_seance_type
                        JOIN LNM_groupe_type
                            ON LNM_groupe_type.id_groupe_type
                                = MAQUETTE_module_sequencage.id_groupe_type
                        WHERE LNM_seance_type.type = 'TP' AND LNM_groupe_type.groupe_type = 'TP'
                        GROUP BY code_module) TPsequenced
                            ON  TPsequenced.code_module = MAQUETTE_module.code_module
                    LEFT JOIN (
                        SELECT code_module, SUM(nombre * duree_h) as hPROJCequenced
                        FROM MAQUETTE_module_sequencage
                        JOIN MAQUETTE_module
                            ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                        JOIN LNM_seance_type
                            ON LNM_seance_type.id_seance_type
                                = MAQUETTE_module_sequencage.id_seance_type
                        JOIN LNM_groupe_type
                            ON LNM_groupe_type.id_groupe_type
                                = MAQUETTE_module_sequencage.id_groupe_type
                        WHERE LNM_seance_type.type = 'PROJ'
                            AND LNM_groupe_type.groupe_type = 'Promo'
                        GROUP BY code_module) PROJsequenced
                            ON  PROJsequenced.code_module = MAQUETTE_module.code_module
                    WHERE MAQUETTE_module.id_responsable = %(id_responsable)s
                    """,
        "params": lambda id_responsable: {"id_responsable": id_responsable},
        "allowedRolesRequester": lambda id_responsable, current_user: (
            [current_user.ExplicitSecondaryK]
            if id_responsable and current_user.id == id_responsable
            else ["administratif", "responsable_etudes"]
        ),
    },
}
