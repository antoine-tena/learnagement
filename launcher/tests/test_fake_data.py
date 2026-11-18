"""Le générateur de données fictives : reproductible, à la bonne taille, sans personne réelle."""

import random
import re

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from launcher.fake_data import FakeDataSize, generate
from launcher.fake_data.accounts import TEST_PASSWORD, hash_test_password
from launcher.fake_data.sql import Raw, literal

MAIL = re.compile(r"'[^']+@([a-z.]+)'")


def test_same_seed_gives_same_file() -> None:
    assert generate(FakeDataSize.SMALL, seed=7) == generate(FakeDataSize.SMALL, seed=7)


def test_other_seed_gives_other_people() -> None:
    assert generate(FakeDataSize.SMALL, seed=7) != generate(FakeDataSize.SMALL, seed=8)


def test_sizes_grow() -> None:
    lengths = [len(generate(size)) for size in FakeDataSize]
    assert lengths == sorted(lengths)
    assert len(set(lengths)) == len(lengths)


def test_every_mail_is_on_the_reserved_domain() -> None:
    domains = set(MAIL.findall(generate(FakeDataSize.MEDIUM)))
    assert domains == {"example.org"}


def test_file_declares_its_encoding() -> None:
    assert "SET NAMES utf8mb4;" in generate(FakeDataSize.SMALL)


def test_test_password_is_checked_like_the_api_does() -> None:
    hashed = hash_test_password(random.Random(1))
    assert PasswordHash((BcryptHasher(),)).verify(TEST_PASSWORD, hashed)


def test_literal_escapes_quotes_and_keeps_raw_sql() -> None:
    assert literal("d'une") == "'d\\'une'"
    assert literal(None) == "NULL"
    assert literal(Raw("(SELECT 1)")) == "(SELECT 1)"
