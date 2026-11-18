from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app
from core.client_address import (
    DEFAULT_TRUSTED_PROXIES,
    ProxySettings,
    client_address_from,
    parse_networks,
)
from core.rate_limit import LOGIN_RATE_LIMIT, limiter

TRUSTED = parse_networks(DEFAULT_TRUSTED_PROXIES)
PHP_FRONT = "10.89.0.5"
TOO_MANY_REQUESTS = 429


def test_trusted_proxy_gives_the_real_client() -> None:
    assert client_address_from(PHP_FRONT, "203.0.113.7", TRUSTED) == "203.0.113.7"


def test_forged_header_from_a_direct_client_is_ignored() -> None:
    assert client_address_from("203.0.113.7", "198.51.100.1", TRUSTED) == "203.0.113.7"


def test_forged_hop_before_the_proxy_is_skipped() -> None:
    forwarded_for = "198.51.100.1, 203.0.113.7"
    assert client_address_from(PHP_FRONT, forwarded_for, TRUSTED) == "203.0.113.7"


def test_trusted_proxies_come_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRUSTED_PROXIES", "192.0.2.0/24, 127.0.0.1/32")
    assert ProxySettings().trusted_proxies == parse_networks("192.0.2.0/24,127.0.0.1/32")


@pytest.fixture
def login_client() -> Iterator[TestClient]:
    limiter.reset()
    with patch("auth.authenticate.authenticate_lnm.login_for_access_token", side_effect=ValueError):
        yield TestClient(app, raise_server_exceptions=False, client=(PHP_FRONT, 50000))
    limiter.reset()


def login_statuses(client: TestClient, forwarded_for: str, count: int) -> list[int]:
    form = {"username": "inconnu", "password": "faux"}
    headers = {"X-Forwarded-For": forwarded_for}
    return [client.post("/token", data=form, headers=headers).status_code for _ in range(count)]


def test_two_clients_behind_the_same_proxy_have_two_counters(login_client: TestClient) -> None:
    threshold = int(LOGIN_RATE_LIMIT.split("/")[0])
    assert login_statuses(login_client, "203.0.113.7", threshold + 1)[-1] == TOO_MANY_REQUESTS
    assert TOO_MANY_REQUESTS not in login_statuses(login_client, "203.0.113.8", 1)
