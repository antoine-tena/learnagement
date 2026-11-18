"""L'adresse du client réel, pour compter la limite de débit par personne et non par proxy.

`X-Forwarded-For` n'est lu que si la requête arrive d'un proxy de confiance (le front PHP, dans le
réseau des conteneurs) ; venu d'ailleurs, l'en-tête est ignoré : un client ne choisit pas son
compteur. La liste se lit de droite à gauche, la première adresse hors des proxys est le client.
"""

from functools import lru_cache
from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode
from starlette.requests import Request

FORWARDED_FOR_HEADER = "x-forwarded-for"
UNKNOWN_CLIENT = "unknown"
# Réseaux des conteneurs (podman : 10.88 et 10.89 ; docker : 172.16/12) et boucle locale du
# développement ; pas tout 10/8, où vivent souvent les VPN.
DEFAULT_TRUSTED_PROXIES = "10.88.0.0/16,10.89.0.0/16,172.16.0.0/12,127.0.0.0/8,::1/128"

type Network = IPv4Network | IPv6Network


def parse_networks(raw: str) -> list[Network]:
    """`10.0.0.0/8,::1/128` en réseaux."""
    return [ip_network(part.strip()) for part in raw.split(",") if part.strip()]


class ProxySettings(BaseSettings):
    trusted_proxies: Annotated[list[Network], NoDecode] = Field(
        default_factory=lambda: parse_networks(DEFAULT_TRUSTED_PROXIES)
    )

    @field_validator("trusted_proxies", mode="before")
    @classmethod
    def split_networks(cls, raw: object) -> object:
        return parse_networks(raw) if isinstance(raw, str) else raw


@lru_cache
def proxy_settings() -> ProxySettings:
    return ProxySettings()


def is_trusted(address: str, trusted: list[Network]) -> bool:
    try:
        parsed = ip_address(address)
    except ValueError:
        return False
    return any(parsed in network for network in trusted)


def client_address_from(peer: str, forwarded_for: str | None, trusted: list[Network]) -> str:
    """Le client réel, vu l'adresse directe `peer` et l'en-tête `X-Forwarded-For`."""
    if not forwarded_for or not is_trusted(peer, trusted):
        return peer
    hops = [hop.strip() for hop in forwarded_for.split(",") if hop.strip()]
    for hop in reversed(hops):
        if not is_trusted(hop, trusted):
            return hop
    return hops[0] if hops else peer


def client_address(request: Request) -> str:
    """Clé de la limite de débit : l'adresse du client réel."""
    peer = request.client.host if request.client else UNKNOWN_CLIENT
    forwarded_for = request.headers.get(FORWARDED_FOR_HEADER)
    return client_address_from(peer, forwarded_for, proxy_settings().trusted_proxies)
