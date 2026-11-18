"""Les personnes fictives : étudiants, enseignants, administratifs et comptes de test."""

import itertools
import random
import unicodedata
from dataclasses import dataclass

from launcher.fake_data.public_set import PUBLIC_COHORTS, PublicCohort
from launcher.fake_data.vocabulary import FAKE_MAIL_DOMAIN, FIRST_NAMES, LAST_NAMES


@dataclass(frozen=True)
class Person:
    """Une personne fictive ; `password` n'est rempli que pour un compte de test."""

    id: int
    first_name: str
    last_name: str
    mail_local_part: str
    password: str | None = None

    @property
    def mail(self) -> str:
        return f"{self.mail_local_part}@{FAKE_MAIL_DOMAIN}"

    @property
    def login(self) -> str:
        """Le login d'un compte interne est son mail : c'est lui que porte le jeton de l'API."""
        return self.mail


@dataclass(frozen=True)
class Student(Person):
    """Un étudiant fictif, inscrit dans une promo du jeu public."""

    cohort: PublicCohort = PUBLIC_COHORTS[0]


def slug(word: str) -> str:
    """Le mot sans accent, en minuscules, bon pour un identifiant ou un mail."""
    decomposed = unicodedata.normalize("NFKD", word.replace("Œ", "Oe").replace("œ", "oe"))
    ascii_word = decomposed.encode("ascii", "ignore").decode()
    return "".join(c for c in ascii_word.lower() if c.isalnum())


class NamePool:
    """Des couples prénom-nom tirés sans remise : chacun ne sert qu'une fois."""

    def __init__(self, rng: random.Random) -> None:
        self._names = list(itertools.product(FIRST_NAMES, LAST_NAMES))
        rng.shuffle(self._names)

    def person(self, person_id: int) -> Person:
        first_name, last_name = self._names.pop()
        return Person(person_id, first_name, last_name, f"{slug(first_name)}.{slug(last_name)}")


def make_teachers(pool: NamePool, count: int) -> list[Person]:
    """Les enseignants fictifs, numérotés à partir de 1."""
    return [pool.person(teacher_id) for teacher_id in range(1, count + 1)]


def make_students(pool: NamePool, per_cohort: int) -> list[Student]:
    """Les étudiants fictifs, `per_cohort` dans chaque promo du jeu public."""
    students: list[Student] = []
    for cohort in PUBLIC_COHORTS:
        for _ in range(per_cohort):
            base = pool.person(len(students) + 1)
            students.append(
                Student(
                    base.id, base.first_name, base.last_name, base.mail_local_part, cohort=cohort
                )
            )
    return students
