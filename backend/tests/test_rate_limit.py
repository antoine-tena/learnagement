from collections.abc import Iterator
from contextlib import nullcontext
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app
from core.rate_limit import ACTIVATION_RATE_LIMIT, LOGIN_RATE_LIMIT, limiter

TOO_MANY_REQUESTS = 429


def threshold(rate_limit: str) -> int:
    return int(rate_limit.split("/")[0])


@pytest.fixture
def client() -> Iterator[TestClient]:
    limiter.reset()
    yield TestClient(app)
    limiter.reset()


def test_activation_confirm_refuses_beyond_its_threshold(client: TestClient) -> None:
    confirm = {"token": "inconnu", "password": "un-mot-de-passe-solide"}
    with (
        patch("domains.account_activation.routes.get_connection", nullcontext),
        patch("domains.account_activation.routes.service.activate", return_value=False),
    ):
        statuses = [
            client.post("/account-activation/confirm", json=confirm).status_code
            for _ in range(threshold(ACTIVATION_RATE_LIMIT) + 1)
        ]
    assert TOO_MANY_REQUESTS not in statuses[:-1]
    assert statuses[-1] == TOO_MANY_REQUESTS


def test_login_refuses_beyond_its_threshold(client: TestClient) -> None:
    form = {"username": "inconnu", "password": "faux"}
    with patch("auth.authenticate.authenticate_lnm.login_for_access_token", side_effect=ValueError):
        statuses = [
            TestClient(app, raise_server_exceptions=False).post("/token", data=form).status_code
            for _ in range(threshold(LOGIN_RATE_LIMIT) + 1)
        ]
    assert TOO_MANY_REQUESTS not in statuses[:-1]
    assert statuses[-1] == TOO_MANY_REQUESTS
