import logging
import sys

from dotenv import load_dotenv
import os
from warnings import deprecated
import pandas as pd
import requests
import io
import json
from urllib.parse import urlsplit

import jwt
from requests import HTTPError, Timeout, RequestException

load_dotenv()

INTERNAL_CERT_PATH = os.path.join(
    os.getenv("DOCKER_SSL_INTERNAL_DIR", "/etc/ssl/learnagement-internal/"), "cert.pem"
)


def get_python_backend_url(endpoint):
    protocol = os.getenv("INSTANCE_PROTOCOL")
    base_url = os.getenv("BACKEND_PYTHON_DOCKER_URL")
    port = os.getenv("BACKEND_PYTHON_DOCKER_PORT")
    url = f"{protocol}://{base_url}:{port}/{endpoint.lstrip('/').rstrip('/')}"
    return url


def get_endpoint(url, token, data=None):
    return python_endpoint("get", url, data, token)


def patch_endpoint(url, data, token):
    return python_endpoint("patch", url, data, token)


def post_endpoint(url, data, token):
    return python_endpoint("post", url, data, token)


def delete_endpoint(url, token):
    return python_endpoint("delete", url, None, token)


def url_without_query(url: str) -> str:
    """L'URL sans ses paramètres, seule partie qui peut aller dans les logs."""
    return urlsplit(url)._replace(query="", fragment="").geturl()


def user_id_of(token: str | None) -> object:
    """L'identifiant de l'utilisateur du jeton, pour les logs ; l'API vérifie le jeton elle-même."""
    try:
        claims = jwt.decode(token or "", options={"verify_signature": False})
    except jwt.InvalidTokenError:
        return None
    return claims.get("id")


def python_endpoint(method, url, data, token):
    """
    Appel de l'API FastAPI

    Args:
        token: Token d'authentification (JWT)

    Returns:
        DataFrame avec les résultats de la requête

    Raises:
        HTTPError: Si le token est invalide (401) ou accès refusé (403)
        RequestException: Pour les autres erreurs réseau
    """

    try:
        # Ni le contenu envoyé ni les paramètres de l'URL : ils portent des noms et des mails
        logging.info("Calling %s %s user_id=%s", method, url_without_query(url), user_id_of(token))
        # Appel au "endpoint" (pas besoin de body car tout est dans la dépendance)
        if method == "get":
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {token}",
            }
            resp = requests.get(
                url, headers=headers, params=data, timeout=30, verify=INTERNAL_CERT_PATH
            )
        elif method == "patch":
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
            resp = requests.patch(
                url, headers=headers, json=data, timeout=30, verify=INTERNAL_CERT_PATH
            )
        elif method == "post":
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
            resp = requests.post(
                url, headers=headers, json=data, timeout=30, verify=INTERNAL_CERT_PATH
            )
        elif method == "delete":
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {token}",
            }
            resp = requests.delete(url, headers=headers, timeout=30, verify=INTERNAL_CERT_PATH)
        else:
            raise Exception(f"Method {method} not supported")

        # Gérer les erreurs HTTP immédiatement après la requête
        if resp.status_code == 401:
            raise HTTPError("Token invalide ou expiré", response=resp)
        elif resp.status_code == 403:
            raise HTTPError("Accès refusé - L'utilisateur n'a pas le rôle requis", response=resp)

        # Gérer les erreurs HTTP
        resp.raise_for_status()

        # Parser la réponse received as string en DataFrame
        # json_string = resp.content.decode('utf-8')
        # print(json_string, flush=True)
        # f json_string != "[]":
        #    url_data = json.loads(json_string)
        #    return pd.read_json(io.StringIO(url_data))
        # else:
        #    return pd.DataFrame()

        # Parser la réponse JSON
        data = resp.json()

        if data and isinstance(data, list):
            return pd.DataFrame(data)
        elif data and isinstance(data, dict) and data["success"]:
            return data["data"]
        else:
            return pd.DataFrame()

    # Le message d'une erreur de requests contient l'URL et ses paramètres : seul son type est
    # journalisé, l'exception remonte entière à l'appelant.
    except Timeout:
        log_call_error("Timeout", method, url, token)
        raise

    except RequestException as error:
        log_call_error(f"Erreur de connexion ({type(error).__name__})", method, url, token)
        raise

    except ValueError:
        log_call_error("Réponse JSON illisible", method, url, token)
        raise

    except Exception as error:
        log_call_error(f"Erreur inattendue ({type(error).__name__})", method, url, token)
        raise


def log_call_error(reason: str, method: str, url: str, token: str | None) -> None:
    """Journalise l'échec d'un appel à l'API sans aucune donnée personnelle."""
    logging.error(
        "%s : %s %s user_id=%s", reason, method, url_without_query(url), user_id_of(token)
    )


def get_enseignants(token):
    url = get_python_backend_url("/enseignants")
    df = get_endpoint(url, token=token)
    return df


def get_etudiants(token):
    url = get_python_backend_url("/etudiants")
    df = get_endpoint(url, token=token)
    return df


def get_filieres(token):
    url = get_python_backend_url("/filieres")
    df = get_endpoint(url, token=token)
    return df


def get_statuts(token):
    url = get_python_backend_url("/statuts")
    df = get_endpoint(url, token=token)
    return df


def get_promos(token):
    url = get_python_backend_url("/promos")
    df = get_endpoint(url, token=token)
    return df


def get_groupe_types(token):
    url = get_python_backend_url("/groupe_types")
    df = get_endpoint(url, token=token)
    return df


def get_seance_types(token):
    url = get_python_backend_url("/seance_types")
    df = get_endpoint(url, token=token)
    return df
