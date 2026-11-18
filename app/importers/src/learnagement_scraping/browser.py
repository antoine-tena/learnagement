"""Le navigateur : ouverture, connexion et parcours des pages."""

import getpass
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from learnagement_scraping.parsers import SITE_URL, next_page

INTRANET_URL = f"{SITE_URL}/intranet/accueil.html"
WAIT_SECONDS = 20
COOKIE_WAIT_SECONDS = 5


@dataclass(frozen=True)
class Credentials:
    login: str
    password: str


def ask_credentials() -> Credentials:
    return Credentials(
        login=input("Entrez votre identifiant : "),
        password=getpass.getpass("Entrez votre mot de passe (l'affichage est caché) : "),
    )


@contextmanager
def open_browser(*, headless: bool) -> Iterator[WebDriver]:
    """Ouvre Chrome et le referme toujours ; Selenium installe seul le pilote."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        driver.quit()


def _accept_cookies(driver: WebDriver) -> None:
    try:
        WebDriverWait(driver, COOKIE_WAIT_SECONDS).until(
            expected_conditions.element_to_be_clickable((By.ID, "tarteaucitronPersonalize"))
        ).click()
    except TimeoutException:
        return


def sign_in(
    driver: WebDriver,
    url: str,
    credentials: Credentials,
    *,
    login_field: str,
    password_field: str,
) -> None:
    """Remplit un formulaire de connexion et attend que le champ de mot de passe disparaisse."""
    driver.get(url)
    _accept_cookies(driver)
    password = driver.find_element(By.NAME, password_field)
    driver.find_element(By.NAME, login_field).send_keys(credentials.login)
    password.send_keys(credentials.password, Keys.RETURN)
    WebDriverWait(driver, WAIT_SECONDS).until(expected_conditions.staleness_of(password))


def sign_in_intranet(driver: WebDriver, credentials: Credentials) -> None:
    sign_in(driver, INTRANET_URL, credentials, login_field="user", password_field="pass")


def sign_in_cas(driver: WebDriver, url: str, credentials: Credentials) -> None:
    sign_in(driver, url, credentials, login_field="username", password_field="password")


def walk_pages[T](driver: WebDriver, path: str, parse: Callable[[str], list[T]]) -> list[T]:
    """Parcourt une liste paginée du site et réunit ce que `parse` lit sur chaque page."""
    result: list[T] = []
    next_path: str | None = path
    while next_path is not None:
        driver.get(f"{SITE_URL}{next_path}")
        html = driver.page_source
        result.extend(parse(html))
        next_path = next_page(html)
    return result
