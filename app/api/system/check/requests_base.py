"""Requêtes SQL de vérification de cohérence (enseignants, modules, séances)."""

BASE_REQUESTS = {
    "get_checkLNM_enseignant_sans_cours": {
        "request": """
            SELECT LNM_enseignant.`prenom`, LNM_enseignant.`nom`, LNM_enseignant.`mail`,
                LNM_enseignant.`statut`, LNM_enseignant.`composante`
            FROM LNM_enseignant
            WHERE LNM_enseignant.id_enseignant
                      NOT IN (  SELECT CLASS_session.id_enseignant
                                FROM CLASS_session
                                WHERE CLASS_session.id_enseignant IS NOT null);""",
        "allowedRolesRequester": ["administratif"],
    },
    "get_checkMAQUETTE_moduleWithoutLearningUnit": {
        "request": """SELECT MAQUETTE_module.`code_module`, MAQUETTE_module.`nom`
            FROM `MAQUETTE_module`
            WHERE `id_module` NOT IN (SELECT `id_module` FROM MAQUETTE_module_as_learning_unit);""",
        "allowedRolesRequester": ["administratif"],
    },
    "get_module_sans_apprentissage_critique": {
        "request": """SELECT MAQUETTE_module.`code_module`, MAQUETTE_module.`nom`
            FROM `MAQUETTE_module`
            WHERE `id_module` NOT IN (SELECT id_module
                FROM APC_apprentissage_critique_as_module);""",
        "allowedRolesRequester": ["administratif"],
    },
    "get_module_detail_ects": {
        "request": """SELECT
                `MAQUETTE_module`.`code_module` AS `code_module`,
                `MAQUETTE_module`.`nom` AS `nom`,
                CAST(`MAQUETTE_module`.`ECTS` AS FLOAT) AS `ECTS`,
                `MAQUETTE_module`.`hCM` AS `hCM`,
                `MAQUETTE_module`.`hTD` AS `hTD`,
                `MAQUETTE_module`.`hTP` AS `hTP`,
                `MAQUETTE_module`.`hPROJ` AS `hPROJ`,
                `MAQUETTE_module`.`hPersonnelle` AS `hPersonnelle`,
                ROUND((ifnull(`MAQUETTE_module`.`hCM`, 0) + ifnull(`MAQUETTE_module`.`hTD`,
                    0) + ifnull(`MAQUETTE_module`.`hTP`, 0)) / `MAQUETTE_module`.`ECTS`,
                    2) AS `h/ECTS`,
                ROUND(`MAQUETTE_module`.`ECTS` / (ifnull(`MAQUETTE_module`.`hCM`,
                    0) + ifnull(`MAQUETTE_module`.`hTD`, 0) + ifnull(`MAQUETTE_module`.`hTP`, 0)),
                    3) AS `ECTS/h`
                FROM `MAQUETTE_module`
                GROUP BY `MAQUETTE_module`.`id_module`
                ORDER BY `MAQUETTE_module`.`code_module`;""",
        "allowedRolesRequester": ["administratif"],
    },
    "get_session_sans_intervenant": {
        "request": """SELECT
                CLASS_session.id_groupe,
                LNM_groupe.nom_groupe,
                LNM_promo.id_promo,
                ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK as promo,
                MAQUETTE_module_sequence.numero_ordre,
                MAQUETTE_module_sequence.id_intervenant_principal,
                MAQUETTE_module_sequence.commentaire,
                MAQUETTE_module_sequencage.id_module,
                MAQUETTE_module_sequencage.id_seance_type,
                CAST(MAQUETTE_module_sequencage.duree_h AS FLOAT) AS duree_h,
                MAQUETTE_module.code_module,
                MAQUETTE_module.nom as nom_module,
                LNM_seance_type.type,
                LNM_semestre.semestre
            FROM CLASS_session
                LEFT JOIN LNM_groupe ON LNM_groupe.id_groupe = CLASS_session.id_groupe
                LEFT JOIN LNM_promo ON LNM_promo.id_promo = LNM_groupe.id_promo
                LEFT JOIN ExplicitSecondaryKs_LNM_promo
                    ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_promo.id_promo
                LEFT JOIN MAQUETTE_module_sequence
                 ON MAQUETTE_module_sequence.id_module_sequence = CLASS_session.id_module_sequence
                LEFT JOIN MAQUETTE_module_sequencage
                 ON MAQUETTE_module_sequencage.id_module_sequencage
                     = MAQUETTE_module_sequence.id_module_sequencage
                LEFT JOIN MAQUETTE_module
                    ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                LEFT JOIN MAQUETTE_module_as_learning_unit
                    ON MAQUETTE_module_as_learning_unit.id_module = MAQUETTE_module.id_module
                LEFT JOIN MAQUETTE_learning_unit
                    ON MAQUETTE_learning_unit.id_learning_unit
                        = MAQUETTE_module_as_learning_unit.id_learning_unit
                        AND MAQUETTE_learning_unit.id_promo = LNM_promo.id_promo
                LEFT JOIN LNM_semestre ON LNM_semestre.id_semestre = MAQUETTE_module.id_semestre
                LEFT JOIN LNM_seance_type
                    ON LNM_seance_type.id_seance_type = MAQUETTE_module_sequencage.id_seance_type
                LEFT JOIN LNM_groupe_type
                    ON LNM_groupe_type.id_groupe_type = MAQUETTE_module_sequencage.id_groupe_type
            WHERE CLASS_session.id_enseignant IS NULL;""",
        "allowedRolesRequester": ["administratif"],
    },
    "get_session_reference_corruption": {
        "request": """
            SELECT
                CLASS_session.`id_session`,
                CLASS_session.`id_module_sequence`,
                MAQUETTE_module_sequence.id_module_sequence
            FROM CLASS_session
            LEFT JOIN MAQUETTE_module_sequence
                ON MAQUETTE_module_sequence.id_module_sequence = CLASS_session.id_module_sequence
            WHERE MAQUETTE_module_sequence.id_module_sequence IS NULL;""",
        "allowedRolesRequester": ["administratif"],
    },
}
