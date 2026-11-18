import logging
import os
from http import HTTPStatus
import jwt
from datetime import datetime, timezone, timedelta

from functools import wraps

from flask import redirect, request, session, jsonify
from dash import Dash, Input, Output, State

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
)

# Cookie posé par le front PHP sur le même hôte : le jeton ne passe pas par l'URL
TOKEN_COOKIE = "lnm_token"
# L'algorithme avec lequel l'API signe ses jetons
JWT_ALGORITHM = "HS256"


def token_from_cookie() -> str | None:
    """Le jeton de la requête en cours, ou None s'il n'y en a pas."""
    return request.cookies.get(TOKEN_COOKIE) or None


def is_token_valid(token, leeway=30):
    """
    Vérifie si le token est valide et non expiré

    Args:
        token: Le JWT à valider

        leeway: Marge en secondes pour l'expiration (utile pour clock skew)

    Returns:
        bool: True si le token est valide, False sinon
    """
    try:
        decode_token(token, leeway)
        return True
    except jwt.InvalidTokenError:
        return False


def decode_token(token, leeway=30):
    """
    Décode le token s'il est valide et non expiré

    Args:
        token: Le JWT à valider

        leeway: Marge en secondes pour l'expiration (utile pour clock skew)

    Returns:
        dict: dictionaire contenant les données du token

    Raises:
        Exception: Si le token est non valide ou expiré
    """

    if not token:
        raise jwt.InvalidTokenError("aucun jeton")
    secret_key = os.getenv("JWT_SIGNING_KEY")
    if not secret_key:
        # Sans la clé de l'API, aucune signature n'est vérifiable : tout jeton est refusé.
        logging.error("Token refusé : JWT_SIGNING_KEY absente de l'environnement")
        raise jwt.InvalidTokenError("JWT_SIGNING_KEY absente")
    try:
        payload = jwt.decode(
            token,
            key=secret_key,
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": True, "verify_exp": True},
            leeway=timedelta(seconds=leeway),
        )

        logging.info("Token valide pour user_id=%s", payload.get("id"))
        return payload

    except jwt.ExpiredSignatureError as e:
        logging.exception("Token expiré")
        raise

    except jwt.InvalidTokenError as e:
        logging.exception(f"Token invalide")
        raise


class FlaskAuth(Dash):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Intercepter toutes les requêtes de callback
        @self.server.before_request
        def check_authentication():
            from flask import request

            # Vérifier si c'est un callback Dash
            if request.path == "/_dash-update-component":
                data = request.get_json(silent=True)

                if data and "output" in data:
                    # Autoriser le callback qui écrit dans 'token'
                    if "token.data" in data["output"]:
                        return  # on laisse passer

                token = session.get("token")

                if not is_token_valid(token):
                    session.pop("token", None)
                    # 204 : Dash n'actualise rien, sans erreur affichée. Au premier chargement,
                    # la barre latérale part avant le callback qui pose le jeton, puis repart.
                    logging.info("Callback refusé : jeton de session absent ou invalide")
                    return "", HTTPStatus.NO_CONTENT
