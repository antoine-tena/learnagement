from unittest.mock import MagicMock

from access_control.responsibilities import (
    _responsibility_covers,
    has_all_responsibilities,
    has_any_of_responsibilities,
    has_hierarchy_responsibilities,
)
from access_control.types import Responsibility
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


def make_required(type_objet: str, **dims: str) -> Responsibility:
    return Responsibility(type_objet=type_objet, dimensions=dims)


# ─────────────────────────────────────────────
# _responsabilite_covers
# ─────────────────────────────────────────────


class TestResponsibilityCovers:
    def test_wildcard_vide(self) -> None:
        """
        {} en BD couvre un scope quelconque.
        """
        stored = make_stored("stage", {})
        required = make_required("stage", filiere="IDU", niveau="FI4")
        assert _responsibility_covers(stored, required) is True

    def test_filiere_couvre_filiere_et_niveau(self) -> None:
        """
        {"filiere":"IDU"} couvre {"filiere":"IDU","niveau":"FI4"}.
        """
        stored = make_stored("stage", {"filiere": "IDU"})
        required = make_required("stage", filiere="IDU", niveau="FI4")
        assert _responsibility_covers(stored, required) is True

    def test_exact_match(self) -> None:
        """
        {"filiere":"IDU","niveau":"FI4"} couvre {"filiere":"IDU","niveau":"FI4"}.
        """
        stored = make_stored("stage", {"filiere": "IDU", "niveau": "FI4"})
        required = make_required("stage", filiere="IDU", niveau="FI4")
        assert _responsibility_covers(stored, required) is True

    def test_une_mauvaise_valeur_ne_couvre_pas(self) -> None:
        """
        {"filiere":"IDU","niveau":"FI4"} ne couvre PAS {"filiere":"IDU","niveau":"FI3"}.
        """
        stored = make_stored("stage", {"filiere": "IDU", "niveau": "FI4"})
        required = make_required("stage", filiere="IDU", niveau="FI3")
        assert _responsibility_covers(stored, required) is False

    def test_trop_precis_ne_couvre_pas(self) -> None:
        """
        {"filiere":"IDU","niveau":"FI4"} ne couvre PAS {"filiere":"IDU"} seul.
        """
        stored = make_stored("stage", {"filiere": "IDU", "niveau": "FI4"})
        required = make_required("stage", filiere="IDU")
        assert _responsibility_covers(stored, required) is False

    def test_mauvaise_valeur_ne_couvre_pas(self) -> None:
        """
        {"filiere":"SEA"} ne couvre PAS {"filiere":"IDU","niveau":"FI4"}.
        """
        stored = make_stored("stage", {"filiere": "SEA"})
        required = make_required("stage", filiere="IDU", niveau="FI4")
        assert _responsibility_covers(stored, required) is False

    def test_dimension_differente_ne_couvre_pas(self) -> None:
        """
        {"filiere":"IDU","semestre":"S8"} ne couvre PAS {"filiere":"IDU","niveau":"FI4"}.
        """
        stored = make_stored("stage", {"filiere": "IDU", "semestre": "S8"})
        required = make_required("stage", filiere="IDU", niveau="FI4")
        assert _responsibility_covers(stored, required) is False

    def test_type_objet_all_couvre_tout(self) -> None:
        """
        type_objet="all" couvre n'importe quel type_objet si dimensions ok.
        """
        stored = make_stored("all", {"filiere": "IDU"})
        required = make_required("stage", filiere="IDU", niveau="FI4")
        assert _responsibility_covers(stored, required) is True

    def test_type_objet_all_ne_couvre_pas_valeur_differente(self) -> None:
        """
        type_objet="all" couvre n'importe quel type_objet si dimensions ok.
        """
        stored = make_stored("all", {"filiere": "SEA"})
        required = make_required("stage", filiere="IDU", niveau="FI4")
        assert _responsibility_covers(stored, required) is False

    def test_type_objet_different_ne_couvre_pas(self) -> None:
        """
        type_objet différent
        """
        stored = make_stored("semestre", {"filiere": "IDU"})
        required = make_required("stage", filiere="IDU")
        assert _responsibility_covers(stored, required) is False

    def test_dimension_a_valeur_any_couvre_plus_large(self) -> None:
        """
        {"filiere":"IDU","niveau":"S8"} couvre {"filiere":"IDU","niveau":"any"}.
        """
        stored = make_stored(
            "stage",
            {
                "filiere": "IDU",
            },
        )
        required = make_required("stage", filiere="any", niveau="FI4")
        assert _responsibility_covers(stored, required) is True

    def test_dimension_a_valeur_any_couvre_exact(self) -> None:
        """
        {"filiere":"IDU","niveau":"S8"} couvre {"filiere":"IDU","niveau":"any"}.
        """
        stored = make_stored("stage", {"filiere": "IDU", "niveau": "FI4"})
        required = make_required("stage", filiere="IDU", niveau="any")
        assert _responsibility_covers(stored, required) is True

    def test_dimension_a_valeur_any_ne_couvre_pas_trop_precis(self) -> None:
        """
        {"filiere":"IDU","niveau":"S8"} couvre {"filiere":"IDU","niveau":"any"}.
        """
        stored = make_stored("stage", {"filiere": "IDU", "niveau": "FI4"})
        required = make_required("stage", filiere="any")
        assert _responsibility_covers(stored, required) is False


# ─────────────────────────────────────────────
# has_any_of_responsabilites
# ─────────────────────────────────────────────


class TestHasAnyOfResponsabilite:
    def test_user_without_responsibility(self) -> None:
        user = make_user(responsibilities=[])
        required = [make_required("stage", filiere="IDU")]

        assert has_any_of_responsibilities(user, required) is False

    def test_user_with_responsibility_covering(self) -> None:
        user = make_user(responsibilities=[make_stored("stage", {"filiere": "IDU"})])
        required = [make_required("stage", filiere="IDU", niveau="FI4")]

        assert has_any_of_responsibilities(user, required) is True

    def test_user_avec_plusieurs_dont_une_couvre(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("stage", {"filiere": "SEA"}),
                make_stored("stage", {"filiere": "IDU"}),
            ]
        )
        required = [make_required("stage", filiere="IDU", niveau="FI4")]

        assert has_any_of_responsibilities(user, required) is True

    def test_user_with_responsibilities_without_covering(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("stage", {"filiere": "SEA"}),
                make_stored("semestre", {"filiere": "IDU", "semestre": "S8"}),
            ]
        )
        required = [make_required("stage", filiere="IDU")]

        assert has_any_of_responsibilities(user, required) is False

    def test_user_couvre_au_moins_une_parmi_plusieurs_required(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("stage", {"filiere": "SEA"}),
                make_stored("stage", {"filiere": "IDU"}),
            ]
        )
        required = [
            make_required("stage", filiere="IDU", niveau="FI4"),
            make_required("stage", filiere="MM", niveau="FI4"),
        ]
        assert has_any_of_responsibilities(user, required) is True


# ─────────────────────────────────────────────
# has_all_responsabilites
# ─────────────────────────────────────────────


class TestHasAllResponsabilites:
    def test_satisfait_toutes(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("filiere", {"filiere": "IDU"}),
                make_stored("semestre", {"filiere": "IDU", "semestre": "S8"}),
            ]
        )
        required = [
            make_required("filiere", filiere="IDU"),
            make_required("semestre", filiere="IDU", semestre="S8"),
        ]
        assert has_all_responsibilities(user, required) is True

    def test_satisfait_une_seule(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("filiere", {"filiere": "IDU"}),
            ]
        )
        required = [
            make_required("filiere", filiere="IDU"),
            make_required("semestre", filiere="IDU", semestre="S8"),
        ]
        assert has_all_responsibilities(user, required) is False

    def test_liste_vide(self) -> None:
        user = make_user(responsibilities=[])
        assert has_all_responsibilities(user, []) is True  # all([]) vacuité


# ─────────────────────────────────────────────
# has_hierarchy_responsabilites
# ─────────────────────────────────────────────


class TestHasHierarchyResponsabilites:
    def setup_method(self) -> None:
        self.hierarchy = [
            make_required("filiere", filiere="IDU"),
            make_required("semestre", filiere="IDU", semestre="S8"),
            make_required("module", filiere="IDU", semestre="S8", niveau="FI4"),
        ]

    def test_satisfait_premier_uniquement(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("filiere", {"filiere": "IDU"}),
            ]
        )
        assert has_hierarchy_responsibilities(user, self.hierarchy) is True

    def test_satisfait_deux_premiers(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("filiere", {"filiere": "IDU"}),
                make_stored("semestre", {"filiere": "IDU", "semestre": "S8"}),
            ]
        )
        assert has_hierarchy_responsibilities(user, self.hierarchy) is True

    def test_satisfait_toute_la_hierarchie(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("filiere", {"filiere": "IDU"}),
                make_stored("semestre", {"filiere": "IDU", "semestre": "S8"}),
                make_stored("module", {"filiere": "IDU", "semestre": "S8", "niveau": "FI4"}),
            ]
        )
        assert has_hierarchy_responsibilities(user, self.hierarchy) is True

    def test_ne_satisfait_pas_le_premier(self) -> None:
        user = make_user(
            responsibilities=[
                make_stored("semestre", {"filiere": "IDU", "semestre": "S8"}),
            ]
        )
        assert has_hierarchy_responsibilities(user, self.hierarchy) is False

    def test_hierarchie_vide(self) -> None:
        user = make_user(responsibilities=[])
        assert has_hierarchy_responsibilities(user, []) is False
