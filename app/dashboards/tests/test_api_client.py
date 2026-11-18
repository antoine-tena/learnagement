"""Le client de l'API des tableaux de bord : URL, jeton transmis, réponses et erreurs, sans réseau."""

from dataclasses import dataclass

import pandas as pd
import pytest
import requests
from requests.exceptions import HTTPError

import app_tools

type Payload = list[dict[str, object]] | dict[str, object]

TOKEN = "jeton-de-test"
URL = "http://api.test/etudiants/1/stages"


class FakeResponse:
    """Une réponse HTTP minimale, à la place de celle de `requests`."""

    def __init__(self, status_code: int, payload: Payload) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Payload:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            # FakeResponse tient lieu de requests.Response, que HTTPError attend
            raise HTTPError(f"HTTP {self.status_code}", response=self)  # type: ignore[arg-type]


@dataclass(frozen=True)
class Call:
    """Un appel reçu par le faux `requests.get`."""

    url: str
    headers: dict[str, str]


def answer_with(monkeypatch: pytest.MonkeyPatch, response: FakeResponse) -> list[Call]:
    """Remplace `requests.get` ; rend la liste des appels reçus."""
    calls: list[Call] = []

    def fake_get(url: str, headers: dict[str, str], **_options: object) -> FakeResponse:
        calls.append(Call(url, headers))
        return response

    monkeypatch.setattr(requests, "get", fake_get)
    return calls


def test_backend_url_joins_protocol_host_port_and_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INSTANCE_PROTOCOL", "https")
    monkeypatch.setenv("BACKEND_PYTHON_DOCKER_URL", "backend")
    monkeypatch.setenv("BACKEND_PYTHON_DOCKER_PORT", "4000")
    url = app_tools.get_python_backend_url("/etudiants/1/stages/")
    assert url == "https://backend:4000/etudiants/1/stages"


def test_get_sends_the_user_token(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = answer_with(monkeypatch, FakeResponse(200, []))
    app_tools.get_endpoint(URL, TOKEN)
    assert calls[0].url == URL
    assert calls[0].headers["Authorization"] == f"Bearer {TOKEN}"


def test_list_answer_becomes_a_table(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = [{"id_stage": 1, "entreprise": "Alpes Logiciels"}]
    answer_with(monkeypatch, FakeResponse(200, rows))
    table = app_tools.get_endpoint(URL, TOKEN)
    assert isinstance(table, pd.DataFrame)
    assert table.to_dict("records") == rows


def test_success_envelope_gives_its_data(monkeypatch: pytest.MonkeyPatch) -> None:
    answer_with(monkeypatch, FakeResponse(200, {"success": True, "data": {"nb": 3}}))
    assert app_tools.get_endpoint(URL, TOKEN) == {"nb": 3}


def test_empty_answer_is_an_empty_table(monkeypatch: pytest.MonkeyPatch) -> None:
    answer_with(monkeypatch, FakeResponse(200, []))
    assert app_tools.get_endpoint(URL, TOKEN).empty


@pytest.mark.parametrize("status_code", [401, 403, 500])
def test_refused_or_failed_call_raises(monkeypatch: pytest.MonkeyPatch, status_code: int) -> None:
    answer_with(monkeypatch, FakeResponse(status_code, {"detail": "non"}))
    with pytest.raises(HTTPError):
        app_tools.get_endpoint(URL, TOKEN)
