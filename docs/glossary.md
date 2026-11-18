# Glossaire

Le code parle anglais, avec les mots du métier ; les textes que lisent les utilisateurs restent en
français (règle [VOCABULARY] de la charte). Ce glossaire fixe, pour chaque mot du métier, le nom
qu'il prend dans le code et la table qui le porte aujourd'hui.

- Pour nommer une variable, une fonction, un fichier ou un dossier, prendre le mot de la colonne
  « Code ». Un mot qui manque s'ajoute ici, dans le commit qui l'utilise.
- Un nom anglais déjà en place et juste est gardé (`learning_unit`, `partner_university`, `wish`).
- Les tables gardent leur nom tant que la base reste en MySQL ; le passage à Postgres (T-39) est
  le moment de les renommer, un schéma par domaine.
- Le dossier d'un domaine porte le même nom dans l'API, le web, les tableaux de bord et le lab.
- Les préfixes `appNN_` (tableaux de bord) et `lnm_` (modules de l'API) disparaissent : ils ne
  disent rien du domaine.

## Les domaines

| Domaine (dossier) | Ce qu'il couvre | Préfixes des tables aujourd'hui |
|---|---|---|
| `people` | étudiants, enseignants, administratifs, rôles, groupes, responsabilités | `LNM_` |
| `curriculum` | maquettes : filières, promos, semestres, UE, modules, séquençage, MCCC | `MAQUETTE_`, `LNM_` |
| `competencies` | approche par compétences (APC) | `APC_` |
| `teaching_load` | charges et prévisionnel des enseignants | (calculées) |
| `timetable` | emploi du temps : séances, séances importées d'ADE, calendriers | `CLASS_`, `EXT_`, `LNM_` |
| `attendance` | absences | `CLASS_` |
| `grades` | évaluations, notes, polypoints | `ETU_`, `LNM_` |
| `deliverables` | rendus attendus dans un module | `LNM_` |
| `internships` | stages | `LNM_` |
| `mobility` | mobilité internationale | `MOB_`, `LNM_` |
| `system` | requêtes et vues stockées en base, d'où l'interface est générée | `MRDBF_`, `VIEW_` |

## Les mots

### Personnes (`people`)

| Métier | Code | Table |
|---|---|---|
| étudiant | `student` | `LNM_etudiant` |
| enseignant | `teacher` | `LNM_enseignant` |
| administratif | `staff` | `LNM_administratif` |
| personne, dans une seule des trois tables (login, mail) | `person` | `LNM_etudiant`, `LNM_enseignant`, `LNM_administratif` |
| utilisateur connecté, quel que soit son rôle | `user` | (modèle `User`) |
| rôle | `role` | `LNM_role`, `LNM_*_as_role` |
| groupe (CM, TD, TP) | `student_group` | `LNM_groupe`, `LNM_etudiant_as_groupe` |
| type de groupe | `group_type` | `LNM_groupe_type` |
| origine (établissement et formation d'avant) | `prior_education` | `LNM_origine` |
| responsabilité (de module, de filière, des études) | `responsibility` | `LNM_responsabilite`, `LNM_enseignant_responsabilites` |

### Maquettes (`curriculum`)

| Métier | Code | Table |
|---|---|---|
| maquette | `curriculum` | |
| filière | `program` | `LNM_filiere` |
| promo | `cohort` | `LNM_promo` |
| parcours | `track` | colonne `parcour` |
| statut de la promo (étudiant ou apprenti, à confirmer) | `study_mode` | `LNM_statut` |
| semestre | `semester` | `LNM_semestre` |
| UE | `learning_unit` | `MAQUETTE_learning_unit` |
| module | `module` | `MAQUETTE_module` |
| discipline | `discipline` | `MAQUETTE_discipline` |
| séquençage d'un module (séances par type) | `module_sequencing` | `MAQUETTE_module_sequencage` |
| séquence | `module_sequence` | `MAQUETTE_module_sequence` |
| dépendance entre séquences | `sequence_dependency` | `MAQUETTE_dependance_sequence` |
| type de séance (CM, TD, TP) | `session_type` | `LNM_seanceType` |
| intervenant principal | `lead_teacher` | colonne `id_intervenant_principal` |
| MCCC | `assessment_rules` | |

### Compétences (`competencies`)

| Métier | Code | Table |
|---|---|---|
| compétence | `competency` | `APC_competence` |
| niveau | `competency_level` | `APC_niveau` |
| apprentissage critique | `critical_learning` | `APC_apprentissage_critique` |
| lien entre un module et un apprentissage critique | `critical_learning_module` | `APC_apprentissage_critique_as_module` |
| composante essentielle | `essential_component` | `APC_composante_essentielle` |
| situation professionnelle | `professional_situation` | `APC_situation_professionnelle` |

### Charges, emploi du temps, absences

| Métier | Code | Table |
|---|---|---|
| charge d'enseignement | `teaching_load` | (calculée) |
| prévisionnel | `forecast` | |
| séance | `class_session` | `CLASS_session` |
| séance prévue, importée d'ADE | `planned_session` | `EXT_seance_planned` |
| lien de calendrier d'une personne | `calendar_link` | `LNM_calendar` |
| absence | `absence` | `CLASS_absence` |
| absentéisme | `absenteeism` | |

### Évaluations et rendus

| Métier | Code | Table |
|---|---|---|
| évaluation | `assessment` | |
| type d'évaluation | `assessment_type` | `LNM_evaluation_type` |
| note | `grade` | `ETU_classical_evaluation` |
| évaluation d'une compétence | `competency_assessment` | `ETU_competence_evaluation` |
| polypoint (nom propre) | `polypoint` | `ETU_polypoint` |
| rendu | `deliverable` | `LNM_rendu_module`, `LNM_rendu_module_as_*` |

### Stages et mobilité

| Métier | Code | Table |
|---|---|---|
| stage | `internship` | `LNM_stage` |
| mobilité | `mobility` | |
| université partenaire | `partner_university` | `MOB_partner_university` |
| places d'une université | `partner_university_places` | `MOB_partner_university_places` |
| quota par filière | `program_quota` | `MOB_filiere_quotas` |
| vœu | `wish` | `MOB_wishes` |
| affectation | `assignment` | `MOB_assignment` |
| campagne de vœux | `campaign` | |
| note de mobilité | `mobility_score` | colonne `mobility_note` |
| redoublant | `repeating_student` | |
| relations internationales | `international_office` | |
| fiche d'université et avis des étudiants | `university` | `LNM_universite` |

### Système (`system`)

| Métier | Code | Table |
|---|---|---|
| requête stockée | `stored_query` | `MRDBF_system_request` |
| vue stockée (affichage, contrôle, modification) | `stored_view` | `VIEW_display`, `VIEW_check`, `VIEW_updatable` |

## À confirmer avec Flavien

- `LNM_statut` : le statut d'une promo (sous statut étudiant ou apprenti) ?
- `MRDBF_` : ce que veut dire le préfixe.
- `LNM_universite` et `MOB_partner_university` : deux tables d'universités, à rapprocher ?
