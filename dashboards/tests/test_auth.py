"""Les tableaux de bord n'acceptent que le jeton signé par l'API, et n'en journalisent rien de personnel."""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import auth

SIGNING_KEY = "cle-de-test-uniquement-pour-les-tableaux-de-bord"
PAYLOAD = {
    "id": 1,
    "login": "etudiant.demo@example.org",
    "email": "etudiant.demo@example.org",
    "firstname": "Étudiant",
    "lastname": "Démo",
}


def signed_token(key: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=5)
    return jwt.encode({**PAYLOAD, "exp": expires}, key, algorithm="HS256")


def test_token_signed_by_the_api_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SIGNING_KEY", SIGNING_KEY)
    assert auth.decode_token(signed_token(SIGNING_KEY))["id"] == 1


def test_token_signed_with_another_key_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SIGNING_KEY", SIGNING_KEY)
    assert not auth.is_token_valid(signed_token("une-autre-cle-forgee-par-un-attaquant"))


def test_without_signing_key_every_token_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SIGNING_KEY", raising=False)
    assert not auth.is_token_valid(signed_token("une-autre-cle-forgee-par-un-attaquant"))


def test_decoded_token_logs_no_personal_data(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("JWT_SIGNING_KEY", SIGNING_KEY)
    with caplog.at_level("DEBUG"):
        auth.decode_token(signed_token(SIGNING_KEY))
    assert "example.org" not in caplog.text
    assert "Démo" not in caplog.text
