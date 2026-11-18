"""Limite de débit des routes publiques, en mémoire de ce processus (sans Redis).

La clé est l'adresse du client réel (`core.client_address`) : un compteur par personne, même
derrière le front PHP.
"""

from slowapi import Limiter

from core.client_address import client_address

LOGIN_RATE_LIMIT = "60/minute"
ACTIVATION_RATE_LIMIT = "10/minute"

limiter = Limiter(key_func=client_address)
