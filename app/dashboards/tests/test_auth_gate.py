"""Un callback Dash ne renvoie rien sans le jeton valide de la session (204 : rien à actualiser)."""

import sys
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from pathlib import Path

import jwt
import pytest
from dash import Input, Output, html
from flask.testing import FlaskClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from auth import FlaskAuth

SIGNING_KEY = "cle-de-test-uniquement-pour-les-tableaux-de-bord"
CALLBACK = {
    "output": "answer.children",
    "outputs": {"id": "answer", "property": "children"},
    "inputs": [{"id": "question", "property": "children", "value": "?"}],
    "changedPropIds": ["question.children"],
}


def signed_token(key: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=5)
    return jwt.encode({"id": 1, "roles": ["etudiant"], "exp": expires}, key, algorithm="HS256")


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> FlaskClient:
    monkeypatch.setenv("JWT_SIGNING_KEY", SIGNING_KEY)
    app = FlaskAuth(__name__)
    app.server.secret_key = SIGNING_KEY
    app.layout = html.Div([html.Div("?", id="question"), html.Div(id="answer")])

    @app.callback(Output("answer", "children"), Input("question", "children"))
    def answer(_question: str) -> str:
        return "reserved-data"

    return app.server.test_client()


def with_session_token(client: FlaskClient, token: str | None) -> FlaskClient:
    with client.session_transaction() as session:
        session["token"] = token
    return client


def test_valid_session_token_runs_the_callback(client: FlaskClient) -> None:
    response = with_session_token(client, signed_token(SIGNING_KEY)).post(
        "/_dash-update-component", json=CALLBACK
    )
    assert response.status_code == 200
    assert "reserved-data" in response.get_data(as_text=True)


def test_forged_session_token_is_refused(client: FlaskClient) -> None:
    response = with_session_token(client, signed_token("cle-forgee")).post(
        "/_dash-update-component", json=CALLBACK
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert "reserved-data" not in response.get_data(as_text=True)


def test_no_session_token_is_refused(client: FlaskClient) -> None:
    response = client.post("/_dash-update-component", json=CALLBACK)
    assert response.status_code == HTTPStatus.NO_CONTENT
