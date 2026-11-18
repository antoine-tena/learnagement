"""Les comptes de test : un par rôle, avec un mot de passe connu, listés dans le README."""

import random
from dataclasses import dataclass

import bcrypt

from launcher.fake_data.public_set import PublicRole

TEST_PASSWORD = "learnagement-fictif"
TEST_LAST_NAME = "Démo"
BCRYPT_PREFIX = b"$2b$12$"
BCRYPT_ALPHABET = "./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
BCRYPT_SALT_LENGTH = 22
BCRYPT_SALT_LAST_CHARACTERS = ".Oeu"


@dataclass(frozen=True)
class TestAccount:
    """Un compte de test : son identifiant, son prénom et, s'il en a un, son rôle."""

    login: str
    first_name: str
    role: PublicRole | None = None


STUDENT_ACCOUNT = TestAccount("etudiant.demo", "Étudiant")
TEACHER_ACCOUNTS = (
    TestAccount("enseignant.demo", "Enseignant"),
    TestAccount("entreprises.demo", "Entreprises", PublicRole.COMPANY_RELATIONS),
)
STAFF_ACCOUNTS = (
    TestAccount("etudes.demo", "Études", PublicRole.STUDIES),
    TestAccount("international.demo", "International", PublicRole.INTERNATIONAL),
    TestAccount("scolarite.demo", "Scolarité", PublicRole.REGISTRAR),
)


def hash_test_password(rng: random.Random) -> str:
    """Le mot de passe de test haché en bcrypt, avec un sel tiré de la graine.

    Le sel vient de `rng` plutôt que du système : la même graine redonne le même fichier.
    """
    body = "".join(rng.choice(BCRYPT_ALPHABET) for _ in range(BCRYPT_SALT_LENGTH - 1))
    salt = BCRYPT_PREFIX + (body + rng.choice(BCRYPT_SALT_LAST_CHARACTERS)).encode()
    return bcrypt.hashpw(TEST_PASSWORD.encode(), salt).decode()
