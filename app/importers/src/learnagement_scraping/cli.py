"""La commande `learnagement-scraping` : un import par sous-commande."""

import csv
import json
from dataclasses import asdict
from pathlib import Path

import click
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from learnagement_scraping import browser, db, parsers

PROGRAMS_TITLE = "Accéder aux programmes"
DIRECTORY_TITLE = "Accéder au Trombinoscope"
TEACHERS_PATH = "/intranet/personnels-enseignants.html"
PERSONAL_SPACE_PATH = "/intranet/pages-speciales/espace-etudiants/espace-personnel.html"
CAS_URL = "https://cas-uds.grenet.fr/login"
GRADES_URL = "https://rvn.grenet.fr/uds/"
PROFILE_LOGIN_URL = "https://intranet.univ-smb.fr/"
PROFILE_URL = "https://monprofil.univ-smb.fr/profil/fr/"


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    click.echo(f"Écrit : {path}")


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        csv.writer(file).writerows(rows)
    click.echo(f"Écrit : {path}")


def _open_programs(driver: WebDriver, credentials: browser.Credentials) -> None:
    browser.sign_in_intranet(driver, credentials)
    path = parsers.link_by_title(driver.page_source, PROGRAMS_TITLE)
    if path is None:
        raise click.ClickException("Lien vers les programmes introuvable.")
    driver.get(f"{parsers.SITE_URL}{path}")


def _read_options(select_id: str, *, headless: bool) -> list[str]:
    credentials = browser.ask_credentials()
    with browser.open_browser(headless=headless) as driver:
        _open_programs(driver, credentials)
        return parsers.select_options(driver.page_source, select_id)


@click.group()
@click.option("--headless", is_flag=True, help="Ne pas afficher le navigateur.")
@click.option(
    "--out",
    type=click.Path(file_okay=False, path_type=Path),
    default=Path("out"),
    show_default=True,
    help="Dossier des fichiers produits (données personnelles : jamais dans git).",
)
@click.pass_context
def cli(context: click.Context, headless: bool, out: Path) -> None:
    """Importe des données depuis l'intranet de Polytech et les services de l'USMB."""
    load_dotenv()
    context.obj = {"headless": headless, "out": out}


@cli.command()
@click.pass_obj
def disciplines(options: dict[str, object]) -> None:
    """Enregistre les disciplines dans la base."""
    names = _read_options("discipline", headless=bool(options["headless"]))
    connection = db.connect()
    try:
        click.echo(f"{db.save_disciplines(connection, names)} disciplines enregistrées.")
    finally:
        connection.close()


@cli.command()
@click.pass_obj
def semestres(options: dict[str, object]) -> None:
    """Enregistre les semestres dans la base."""
    labels = _read_options("semestre", headless=bool(options["headless"]))
    connection = db.connect()
    try:
        click.echo(f"{db.save_semesters(connection, labels)} semestres enregistrés.")
    finally:
        connection.close()


@cli.command()
@click.pass_obj
def enseignants(options: dict[str, object]) -> None:
    """Crée les enseignants de l'annuaire dans la base."""
    credentials = browser.ask_credentials()
    with browser.open_browser(headless=bool(options["headless"])) as driver:
        browser.sign_in_intranet(driver, credentials)
        found = browser.walk_pages(driver, TEACHERS_PATH, parsers.teachers)
    connection = db.connect()
    try:
        count = db.save_teachers(
            connection,
            [(teacher.prenom, teacher.nom, teacher.mail) for teacher in found],
        )
        click.echo(f"{count} enseignants enregistrés.")
    finally:
        connection.close()


@cli.command()
@click.pass_obj
def etudiants(options: dict[str, object]) -> None:
    """Exporte le trombinoscope en CSV et en JSON."""
    out = options["out"]
    assert isinstance(out, Path)
    credentials = browser.ask_credentials()
    with browser.open_browser(headless=bool(options["headless"])) as driver:
        browser.sign_in_intranet(driver, credentials)
        path = parsers.link_by_title(driver.page_source, DIRECTORY_TITLE)
        if path is None:
            raise click.ClickException("Lien vers le trombinoscope introuvable.")
        found = browser.walk_pages(driver, path, parsers.students)
    _write_csv(
        out / "etudiants.csv",
        [[item.annee, item.filiere, item.nom, item.prenom] for item in found],
    )
    _write_json(out / "etudiants.json", [asdict(item) for item in found])


@cli.command()
@click.option("--promotion", default="2021-2025", show_default=True)
@click.option("--filiere", default="idu_4", show_default=True)
@click.pass_obj
def modules(options: dict[str, object], promotion: str, filiere: str) -> None:
    """Exporte les fiches des modules et met à jour leurs volumes horaires dans la base."""
    out = options["out"]
    assert isinstance(out, Path)
    credentials = browser.ask_credentials()
    details: dict[str, dict[str, str]] = {}
    with browser.open_browser(headless=bool(options["headless"])) as driver:
        _open_programs(driver, credentials)
        driver.find_element(By.ID, promotion).click()
        driver.find_element(By.ID, filiere).click()
        driver.find_element(By.NAME, "tx_savfilters_default[submit]").submit()
        for link in parsers.module_links(driver.page_source):
            driver.get(link.url)
            details[link.code] = {
                "Matiere": link.nom,
                **parsers.module_details(driver.page_source),
            }
    _write_json(out / "modules.json", details)
    connection = db.connect()
    try:
        for code, module in details.items():
            db.save_module_hours(connection, code, module)
    finally:
        connection.close()
    click.echo(f"{len(details)} modules traités.")


@cli.command()
@click.pass_obj
def profil(options: dict[str, object]) -> None:
    """Exporte le nom, le prénom et la date de naissance de l'étudiant connecté."""
    out = options["out"]
    assert isinstance(out, Path)
    credentials = browser.ask_credentials()
    with browser.open_browser(headless=bool(options["headless"])) as driver:
        browser.sign_in_cas(driver, PROFILE_LOGIN_URL, credentials)
        driver.get(f"{PROFILE_URL}{credentials.login}")
        found = parsers.profile(driver.page_source)
    if found is None:
        raise click.ClickException("Informations du profil introuvables.")
    _write_json(out / "profil.json", asdict(found))


@cli.command()
@click.pass_obj
def notes(options: dict[str, object]) -> None:
    """Exporte le relevé de notes de l'étudiant connecté."""
    out = options["out"]
    assert isinstance(out, Path)
    credentials = browser.ask_credentials()
    with browser.open_browser(headless=bool(options["headless"])) as driver:
        browser.sign_in_cas(driver, CAS_URL, credentials)
        driver.get(GRADES_URL)
        found = parsers.grades(driver.page_source)
    _write_json(out / "notes.json", found)


@cli.command()
@click.pass_obj
def stages(options: dict[str, object]) -> None:
    """Exporte les polypoints et les stages de l'étudiant connecté."""
    out = options["out"]
    assert isinstance(out, Path)
    credentials = browser.ask_credentials()
    with browser.open_browser(headless=bool(options["headless"])) as driver:
        browser.sign_in_intranet(driver, credentials)
        driver.get(f"{parsers.SITE_URL}{PERSONAL_SPACE_PATH}")
        html = driver.page_source
    _write_json(
        out / "stages.json",
        {
            "polypoints": [asdict(item) for item in parsers.polypoints(html)],
            "stages": [asdict(item) for item in parsers.internships(html)],
        },
    )
