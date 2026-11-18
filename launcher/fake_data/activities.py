"""La vie fictive des promos : stages, vœux de mobilité, séances et absences."""

import random
from datetime import date, datetime, time, timedelta

from launcher.fake_data.people import Person, Student
from launcher.fake_data.public_set import (
    COHORT_GROUP_TYPE,
    LECTURE_SESSION_TYPE,
    PUBLIC_PARTNER_UNIVERSITIES,
    partner_university_id,
)
from launcher.fake_data.sql import Raw, SqlValue, insert
from launcher.fake_data.vocabulary import (
    CITIES,
    COMPANIES,
    INTERNSHIP_TITLES,
    InternshipNature,
)

INTERNSHIP_YEARS = {4: InternshipNature.ASSISTANT_ENGINEER, 5: InternshipNature.END_OF_STUDIES}
INTERNSHIP_WEEKS = {4: 12, 5: 24}
MOBILITY_YEAR = 4
MOBILITY_SEMESTER = 8
WISHES_PER_STUDENT = 3
LECTURES_PER_MODULE = 4
LECTURE_HOURS = 2
ABSENCE_ONE_IN = 15
SCHOOL_YEAR_START = date(2026, 9, 7)
SESSION_HOUR = time(8)
COUNTRY = "France"


def internships(rng: random.Random, students: list[Student], teachers: list[Person]) -> str:
    """Un stage par étudiant de 4e et 5e année, suivi par un enseignant."""
    placements = [
        (company, city) for company in COMPANIES for city in CITIES
    ]  # (entreprise, ville) : l'entreprise et l'intitulé forment une clé unique
    rows: list[list[SqlValue]] = []
    for index, student in enumerate(s for s in students if s.cohort.year in INTERNSHIP_YEARS):
        company, (city, postcode) = placements[index % len(placements)]
        title = rng.choice(INTERNSHIP_TITLES)
        start = date(2027, 4, 5) + timedelta(weeks=rng.randrange(4))
        weeks = INTERNSHIP_WEEKS[student.cohort.year]
        rows.append([
            f"{company} — {city}", f"{title} {index + 1}", f"Stage fictif : {title.lower()}.",
            None, city, postcode, COUNTRY, start, start + timedelta(weeks=weeks),
            INTERNSHIP_YEARS[student.cohort.year].value, student.id, rng.choice(teachers).id,
        ])  # fmt: skip
    columns = (
        "entreprise", "intitulé", "description", "adresse", "ville", "code_postal", "pays",
        "date_debut", "date_fin", "nature", "id_etudiant", "id_enseignant",
    )  # fmt: skip
    return insert("LNM_stage", columns, rows)


def mobility_wishes(rng: random.Random, students: list[Student]) -> str:
    """Trois vœux d'universités partenaires distinctes par étudiant de 4e année."""
    rows: list[list[SqlValue]] = []
    for student in (s for s in students if s.cohort.year == MOBILITY_YEAR):
        ranks = rng.sample(range(PUBLIC_PARTNER_UNIVERSITIES), WISHES_PER_STUDENT)
        submitted = datetime.combine(SCHOOL_YEAR_START + timedelta(days=rng.randrange(60)), time(9))
        for priority, rank in enumerate(ranks, start=1):
            rows.append(
                [student.id, partner_university_id(rank), MOBILITY_SEMESTER, priority, submitted]
            )
    columns = (
        "id_etudiant", "id_partner_university", "id_semestre", "priority", "submission_date"
    )  # fmt: skip
    return insert("MOB_wishes", columns, rows)


def lectures(teacher_count: int) -> str:
    """Des cours magistraux pour chaque module rattaché à une promo.

    Les triggers de la base en tirent les séquences, puis une séance par groupe promo.
    """
    teacher = Raw(f"1 + MOD(m.`id_module`, {teacher_count})")
    return (
        "INSERT INTO `MAQUETTE_module_sequencage` (`id_module`, `nombre`, `id_seance_type`, "
        "`id_groupe_type`, `duree_h`, `id_intervenant_principal`)\n"
        f"SELECT DISTINCT m.`id_module`, {LECTURES_PER_MODULE}, {LECTURE_SESSION_TYPE}, "
        f"{COHORT_GROUP_TYPE}, {LECTURE_HOURS}, {teacher}\n"
        "FROM `MAQUETTE_module` m\n"
        "JOIN `MAQUETTE_module_as_learning_unit` USING (`id_module`);\n"
    )


def session_schedule_and_absences(seed: int) -> str:
    """Une date pour chaque séance, puis quelques absences, tirées de la graine en SQL."""
    return (
        "UPDATE `CLASS_session` SET `schedule` = "
        f"TIMESTAMP('{SCHOOL_YEAR_START.isoformat()}', '{SESSION_HOUR.isoformat()}') "
        "+ INTERVAL MOD(`id_session`, 150) DAY;\n"
        "INSERT INTO `CLASS_absence` (`id_session`, `id_etudiant`)\n"
        "SELECT s.`id_session`, g.`id_etudiant`\n"
        "FROM `CLASS_session` s\n"
        "JOIN `LNM_etudiant_as_groupe` g USING (`id_groupe`)\n"
        f"WHERE MOD(s.`id_session` * 31 + g.`id_etudiant` * 17 + {seed}, {ABSENCE_ONE_IN}) = 0;\n"
    )
