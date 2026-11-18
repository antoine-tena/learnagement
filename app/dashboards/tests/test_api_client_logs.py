"""Les logs du client de l'API : méthode, URL sans paramètres et user_id, jamais le contenu envoyé."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
import requests

import app_tools

URL = "http://api.test/etudiants"
PERSONAL = {"nom": "Démo", "prenom": "Étudiant", "mail": "etudiant.demo@example.org"}
PERSONAL_WORDS = ("Démo", "Étudiant", "example.org")


class OkResponse:
    status_code = 200

    def json(self) -> list[dict[str, str]]:
        return []

    def raise_for_status(self) -> None:
        return None


def token_of(user_id: int) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=5)
    return jwt.encode({"id": user_id, "exp": expires}, "cle-de-test", algorithm="HS256")


def answer_ok(_url: str, **_options: object) -> OkResponse:
    return OkResponse()


@pytest.mark.parametrize("method", ["get", "post", "patch"])
def test_sent_content_is_not_logged(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, method: str
) -> None:
    monkeypatch.setattr(requests, method, answer_ok)
    with caplog.at_level("DEBUG"):
        app_tools.python_endpoint(method, URL, PERSONAL, token_of(7))
    for word in PERSONAL_WORDS:
        assert word not in caplog.text


def test_failed_call_logs_no_personal_data(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def refuse(url: str, **_options: object) -> None:
        # requests met l'URL complète, paramètres compris, dans le message de ses erreurs
        raise requests.ConnectionError(f"Max retries exceeded with url: {url}?nom=Démo")

    monkeypatch.setattr(requests, "get", refuse)
    with caplog.at_level("DEBUG"), pytest.raises(requests.ConnectionError):
        app_tools.python_endpoint("get", URL, PERSONAL, token_of(7))
    for word in PERSONAL_WORDS:
        assert word not in caplog.text
    assert "user_id=7" in caplog.text


def test_log_keeps_method_url_and_user_id(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(requests, "get", answer_ok)
    with caplog.at_level("INFO"):
        app_tools.python_endpoint("get", f"{URL}?mail=etudiant.demo@example.org", None, token_of(7))
    assert "get http://api.test/etudiants" in caplog.text
    assert "user_id=7" in caplog.text
    assert "example.org" not in caplog.text
