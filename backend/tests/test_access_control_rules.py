from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from access_control.checker import check_access
from access_control.rules import evaluate_rule
from models.request import SQLRequest
from models.user import User


def make_user(type_role: str = "enseignant", responsibilities: list[dict] | None = None) -> User:
    user = MagicMock()
    user.type = type_role
    user.roles = [type_role]
    user.id = 99
    user.responsibilities = responsibilities or []
    return user


def make_stored(type_objet: str, dimensions: dict) -> dict:
    return {"type_objet": type_objet, "dimensions": dimensions}


# ─────────────────────────────────────────────
# evaluate_rule
# ─────────────────────────────────────────────


class TestEvaluateRule:
    def test_anonymous_autorise_toujours(self) -> None:
        assert evaluate_rule("anonymous", None, {}) is True

    def test_connected_user_avec_user(self) -> None:
        assert evaluate_rule("connected_user", make_user(), {}) is True

    def test_connected_user_sans_user(self) -> None:
        assert evaluate_rule("connected_user", None, {}) is False

    def test_string_inconnue_leve_erreur(self) -> None:
        with pytest.raises(ValueError):
            evaluate_rule("superadmin", make_user(), {})

    def test_liste_roles_role_present(self) -> None:
        user = make_user(type_role="administratif")
        assert evaluate_rule(["administratif", "enseignant"], user, {}) is True

    def test_liste_roles_role_absent(self) -> None:
        user = make_user(type_role="etudiant")
        assert evaluate_rule(["administratif", "enseignant"], user, {}) is False

    def test_liste_roles_vide_retourne_false(self) -> None:
        assert evaluate_rule([], make_user(), {}) is False

    def test_liste_roles_user_none(self) -> None:
        assert evaluate_rule(["administratif"], None, {}) is False

    def test_dict_roles_satisfait(self) -> None:
        user = make_user(type_role="administratif")
        assert evaluate_rule({"roles": ["administratif"]}, user, {}) is True

    def test_dict_any_satisfait(self) -> None:
        user = make_user(responsibilities=[make_stored("stage", {"filiere": "IDU"})])
        rule = {"any": [{"type_objet": "stage", "filiere": "IDU"}]}
        assert evaluate_rule(rule, user, {}) is True

    def test_dict_any_non_satisfait(self) -> None:
        user = make_user(responsibilities=[make_stored("stage", {"filiere": "SEA"})])
        rule = {"any": [{"type_objet": "stage", "filiere": "IDU"}]}
        assert evaluate_rule(rule, user, {}) is False

    def test_dict_all_satisfait(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("filiere", {"filiere": "IDU"}),
                make_stored("semestre", {"semestre": "S8"}),
            ]
        )
        rule = {
            "all": [
                {"type_objet": "filiere", "filiere": "IDU"},
                {"type_objet": "semestre", "semestre": "S8"},
            ]
        }
        assert evaluate_rule(rule, user, {}) is True

    def test_dict_au_moins_une_condition_suffit(self) -> None:
        """roles échoue mais one réussit → True"""
        user = make_user(
            type_role="enseignant", responsibilities=[make_stored("stage", {"filiere": "IDU"})]
        )
        rule = {
            "roles": ["administratif"],
            "any": [{"type_objet": "stage", "filiere": "IDU"}],
        }
        assert evaluate_rule(rule, user, {}) is True

    def test_dict_cle_inconnue_leve_erreur(self) -> None:
        with pytest.raises(ValueError):
            evaluate_rule({"superpower": ["x"]}, make_user(), {})

    def test_lambda_retourne_string(self) -> None:
        assert evaluate_rule(lambda params, user: "anonymous", None, {}) is True

    def test_lambda_retourne_liste_roles(self) -> None:
        user = make_user(type_role="administratif")

        def rule(params: dict, user: User) -> list[str]:
            return ["administratif"] if params.get("secret") else ["etudiant"]

        assert evaluate_rule(rule, user, {"secret": True}) is True

    def test_lambda_utilise_params(self) -> None:
        user = make_user(type_role="etudiant")
        user.id = 42

        def rule(params: dict, u: User) -> str | list[str]:
            return "connected_user" if u.id == params.get("id_etudiant") else ["administratif"]

        assert evaluate_rule(rule, user, {"id_etudiant": 42}) is True
        assert evaluate_rule(rule, user, {"id_etudiant": 99}) is False


# ─────────────────────────────────────────────
# check_access
# ─────────────────────────────────────────────


class TestCheckAccess:
    def setup_method(self) -> None:
        self.requests = {
            "get_public": {
                "request": "SELECT 1",
                "params": {},
                "allowedRolesRequester": "anonymous",
            },
            "get_admin_only": {
                "request": "SELECT 1",
                "params": {},
                "allowedRolesRequester": ["administratif"],
            },
        }

    def test_acces_autorise(self) -> None:
        request = SQLRequest.model_validate(self.requests["get_public"])
        check_access(request, None)  # ne lève pas d'exception

    def test_acces_refuse_leve_403(self) -> None:
        request = SQLRequest.model_validate(self.requests["get_admin_only"])
        user = make_user(type_role="etudiant")
        with pytest.raises(HTTPException) as exc:
            check_access(request, user)
        assert exc.value.status_code == 403
