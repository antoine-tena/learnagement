"""L'assemblage du fichier SQL fictif, table par table, dans l'ordre des clés étrangères."""

import random
from enum import StrEnum

from launcher.fake_data import activities
from launcher.fake_data.accounts import (
    STAFF_ACCOUNTS,
    STUDENT_ACCOUNT,
    TEACHER_ACCOUNTS,
    TEST_LAST_NAME,
    TestAccount,
    hash_test_password,
)
from launcher.fake_data.people import NamePool, Person, Student, make_students, make_teachers
from launcher.fake_data.public_set import (
    COHORT_GROUP_TYPE,
    PUBLIC_COHORTS,
    PublicCohort,
    cohort_id,
    role_id,
)
from launcher.fake_data.sql import Raw, SqlValue, insert
from launcher.fake_data.vocabulary import COMPONENT

DEFAULT_SEED = 2026
FAKE_DATA_FILE_NAME = "V0.99.9__fake_data.sql"
TEST_STUDENT_COHORT = PublicCohort("IDU", 4)


class FakeDataSize(StrEnum):
    """Les tailles du jeu fictif : de quoi cliquer, de quoi tester, de quoi mesurer."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


STUDENTS_PER_COHORT = {FakeDataSize.SMALL: 8, FakeDataSize.MEDIUM: 25, FakeDataSize.LARGE: 80}
TEACHER_COUNT = {FakeDataSize.SMALL: 15, FakeDataSize.MEDIUM: 40, FakeDataSize.LARGE: 120}


def account_person(account: TestAccount, person_id: int, password_hash: str) -> Person:
    """La personne derrière un compte de test."""
    return Person(
        person_id, account.first_name, TEST_LAST_NAME, account.mail_local_part, password_hash
    )


def people_sql(students: list[Student], teachers: list[Person], staff: list[Person]) -> str:
    """Les étudiants, leur groupe promo, les enseignants et les administratifs."""
    student_rows: list[list[SqlValue]] = [
        [s.id, s.last_name, s.first_name, s.mail, s.login, s.password, cohort_id(s.cohort)]
        for s in students
    ]
    group_rows: list[list[SqlValue]] = [
        [s.id, Raw(
            f"(SELECT `id_groupe` FROM `LNM_groupe` WHERE `id_promo` = {cohort_id(s.cohort)} "
            f"AND `id_groupe_type` = {COHORT_GROUP_TYPE})"
        )]
        for s in students
    ]  # fmt: skip
    person_columns = ("nom", "prenom", "mail", "login", "password")
    return "".join((
        insert(
            "LNM_enseignant",
            ("id_enseignant", *person_columns, "composante"),
            [[t.id, t.last_name, t.first_name, t.mail, t.login, t.password, COMPONENT]
             for t in teachers],
        ),
        insert(
            "LNM_administratif",
            ("id_administratif", *person_columns),
            [[a.id, a.last_name, a.first_name, a.mail, a.login, a.password] for a in staff],
        ),
        insert("LNM_etudiant", ("id_etudiant", *person_columns, "id_promo"), student_rows),
        insert("LNM_etudiant_as_groupe", ("id_etudiant", "id_groupe"), group_rows),
    ))  # fmt: skip


def roles_sql(teachers: list[Person], staff: list[Person]) -> str:
    """Les rôles des comptes de test, retrouvés par leur nom dans le jeu public."""
    teacher_roles: list[list[SqlValue]] = [
        [teachers[index].id, role_id(account.role)]
        for index, account in enumerate(TEACHER_ACCOUNTS)
        if account.role is not None
    ]
    staff_roles: list[list[SqlValue]] = [
        [staff[index].id, role_id(account.role)]
        for index, account in enumerate(STAFF_ACCOUNTS)
        if account.role is not None
    ]
    return insert("LNM_enseignant_as_role", ("id_enseignant", "id_role"), teacher_roles) + insert(
        "LNM_administratif_as_role", ("id_administratif", "id_role"), staff_roles
    )


def build_people(
    rng: random.Random, size: FakeDataSize
) -> tuple[list[Student], list[Person], list[Person]]:
    """Les étudiants, enseignants et administratifs, comptes de test en tête de chaque liste."""
    password_hash = hash_test_password(rng)
    pool = NamePool(rng)
    test_teachers = [
        account_person(account, index, password_hash)
        for index, account in enumerate(TEACHER_ACCOUNTS, start=1)
    ]
    teachers = test_teachers + [
        Person(p.id + len(test_teachers), p.first_name, p.last_name, p.mail_local_part)
        for p in make_teachers(pool, TEACHER_COUNT[size])
    ]
    staff = [
        account_person(account, index, password_hash)
        for index, account in enumerate(STAFF_ACCOUNTS, start=1)
    ]
    test_student = account_person(STUDENT_ACCOUNT, 1, password_hash)
    students = [Student(**vars(test_student), cohort=TEST_STUDENT_COHORT)] + [
        Student(s.id + 1, s.first_name, s.last_name, s.mail_local_part, cohort=s.cohort)
        for s in make_students(pool, STUDENTS_PER_COHORT[size])
    ]
    return students, teachers, staff


def generate(size: FakeDataSize, seed: int = DEFAULT_SEED) -> str:
    """Le fichier SQL fictif de cette taille, toujours le même pour la même graine."""
    rng = random.Random(seed)
    students, teachers, staff = build_people(rng, size)
    header = (
        f"-- Données fictives Learnagement : taille {size.value}, graine {seed}.\n"
        f"-- {len(PUBLIC_COHORTS)} promos du jeu public, aucune personne réelle.\n"
        "-- Produit par `python Learnagement.py fake-data` : ne pas éditer à la main.\n"
        "SET NAMES utf8mb4;\n\n"
    )
    return "\n".join((
        header,
        people_sql(students, teachers, staff),
        roles_sql(teachers, staff),
        activities.internships(rng, students, teachers),
        activities.mobility_wishes(rng, students),
        activities.lectures(len(teachers)),
        activities.session_schedule_and_absences(seed),
    ))  # fmt: skip
