"""Extraction des données depuis le HTML des pages : aucun réseau, aucune base."""

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

SITE_URL = "https://www.polytech.univ-smb.fr"
MODULE_LINK_MIN_LENGTH = 200
PLACEHOLDER_OPTION = "---"
GRADE_FIELDS = (
    "Note_dividende",
    "Note_diviseur",
    "Pts jury",
    "Année",
    "Session",
    "Résultat",
    "Crédit",
    "Classement",
)

type GradeRow = dict[str, str]


@dataclass(frozen=True)
class Teacher:
    nom: str
    prenom: str
    mail: str


@dataclass(frozen=True)
class Student:
    annee: str
    filiere: str
    nom: str
    prenom: str


@dataclass(frozen=True)
class ModuleLink:
    code: str
    nom: str
    url: str


@dataclass(frozen=True)
class Profile:
    nom: str
    prenom: str
    naissance: str


@dataclass(frozen=True)
class Polypoint:
    intitule: str
    tache: str
    nb_points: str
    annee: str


@dataclass(frozen=True)
class Internship:
    entreprise: str
    ville: str
    date_debut: str
    date_fin: str


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def _text(parent: Tag, css: str) -> str | None:
    found = parent.select_one(css)
    return None if found is None else found.get_text()


def select_options(html: str, select_id: str) -> list[str]:
    """Les choix d'une liste déroulante, sans le choix vide `---`."""
    options = _soup(html).select(f"select#{select_id} option")
    labels = [option.get_text().strip() for option in options]
    return [label for label in labels if label and label != PLACEHOLDER_OPTION]


def link_by_title(html: str, title: str) -> str | None:
    found = _soup(html).find("a", title=title)
    return str(found["href"]) if isinstance(found, Tag) and found.has_attr("href") else None


def next_page(html: str) -> str | None:
    """Le chemin de la page suivante d'une liste paginée, sans le domaine du site."""
    found = _soup(html).find("a", href=re.compile("nextPage"))
    if not isinstance(found, Tag):
        return None
    return str(found["href"]).replace(SITE_URL, "")


def teachers(html: str) -> list[Teacher]:
    result = []
    for card in _soup(html).select(".info"):
        name = _text(card, ".name")
        mail = _text(card, ".email")
        if name is None or mail is None or len(name.split()) < 2:
            continue
        nom, prenom = name.split()[:2]
        result.append(Teacher(nom=nom, prenom=prenom, mail=mail.removeprefix("Mail :").strip()))
    return result


def students(html: str) -> list[Student]:
    """Le trombinoscope : un statut `FI4 - EIT` et un nom suivi du prénom."""
    result = []
    for card in _soup(html).select(".etudiant"):
        status = _text(card, ".statut")
        name = _text(card, ".name")
        if status is None or name is None:
            continue
        status_parts = status.split()
        name_parts = name.split()
        if len(status_parts) < 3 or len(name_parts) < 2:
            continue
        result.append(
            Student(
                annee=status_parts[0],
                filiere=status_parts[2],
                nom=name_parts[0],
                prenom=name_parts[1],
            )
        )
    return result


def module_links(html: str) -> list[ModuleLink]:
    """Les modules d'un programme, reconnus à leur très long lien, avec le code de même rang."""
    soup = _soup(html)
    codes = soup.select("li.code")
    links = [
        link for link in soup.select("a[href]") if len(str(link["href"])) > MODULE_LINK_MIN_LENGTH
    ]
    return [
        ModuleLink(
            code=code.get_text().strip().removeprefix("Code").strip(" :\n\t"),
            nom=link.get_text().strip(),
            url=f"{SITE_URL}{link['href']}",
        )
        for code, link in zip(codes, links, strict=False)
    ]


def module_details(html: str) -> dict[str, str]:
    """Les couples intitulé et valeur d'une fiche de module."""
    soup = _soup(html)
    labels = [div.get_text(strip=True) for div in soup.select("div.label")]
    values = [div.get_text(strip=True) for div in soup.select("div.value")]
    return {label: value for label, value in zip(labels, values, strict=False) if label and value}


def profile(html: str) -> Profile | None:
    table = _soup(html).select_one("table.table.table-bordered.table-condensed")
    if table is None:
        return None
    values: dict[str, str] = {}
    for header in table.select("th"):
        cell = header.find_next("td")
        if isinstance(cell, Tag):
            values[header.get_text().strip()] = cell.get_text().strip()
    try:
        return Profile(
            nom=values["Nom usuel"],
            prenom=values["Prénom"],
            naissance=values["Date de naissance"],
        )
    except KeyError:
        return None


def grades(html: str) -> list[dict[str, str | list[GradeRow]]]:
    """Le relevé de notes : une ligne en gras par UE, suivie des lignes de ses matières."""
    table = _soup(html).select_one("table#tableau")
    if table is None:
        return []
    units: list[dict[str, str | list[GradeRow]]] = []
    subjects: list[GradeRow] = []
    for row in table.select("tr")[1:-1]:
        cells = row.select("td")
        if not cells:
            continue
        values: GradeRow = {"Epreuve": cells[0].get_text().strip()}
        for field, cell in zip(GRADE_FIELDS, cells[1:], strict=False):
            values[field] = cell.get_text().replace(" ", "").strip()
        if cells[0].select_one("b") is not None:
            subjects = []
            units.append({**values, "Matières": subjects})
        else:
            subjects.append(values)
    return units


def polypoints(html: str) -> list[Polypoint]:
    result = []
    for block in _soup(html).select("div.value"):
        intitule = _text(block, "li.intitule")
        tache = _text(block, "li.intitule_tache")
        nb_points = _text(block, "li.nb_points")
        annee = _text(block, "li.annee")
        if intitule is None or tache is None or nb_points is None or annee is None:
            continue
        result.append(Polypoint(intitule, tache, nb_points, annee))
    return result


def _iso_date(french_date: str) -> str:
    day, month, year = french_date.split("/")
    return f"{year}-{month}-{day}"


def internships(html: str) -> list[Internship]:
    result = []
    for block in _soup(html).select("div.value"):
        company = _text(block, "li.entreprise")
        period = _text(block, "li.date")
        if company is None or period is None or " - " not in company:
            continue
        dates = re.findall(r"\d{2}/\d{2}/\d{4}", period)
        if len(dates) < 2:
            continue
        entreprise, ville = company.split(" - ", 1)
        result.append(Internship(entreprise, ville, _iso_date(dates[0]), _iso_date(dates[1])))
    return result
