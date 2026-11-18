"""Limite de débit des routes publiques, en mémoire de ce processus (sans Redis).

La clé est l'adresse vue par l'API : derrière le front PHP ou le proxy Next, toutes les requêtes
d'un même front partagent donc le même compteur. Les seuils en tiennent compte.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

LOGIN_RATE_LIMIT = "60/minute"
ACTIVATION_RATE_LIMIT = "10/minute"

limiter = Limiter(key_func=get_remote_address)
