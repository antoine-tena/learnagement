"""Le jeu fictif posé dans `database/data` : par la commande, ou proposé au premier lancement."""

from pathlib import Path

from click.testing import CliRunner

from launcher.cli import cli
from launcher.fake_data import FAKE_DATA_FILE_NAME
from launcher.fake_data.install import offer_fake_data
from launcher.fake_data.public_set import PUBLIC_SET_DIR

PUBLIC_FILE_NAMES = {path.name for path in PUBLIC_SET_DIR.glob("V*.sql")}


def written_files(data_dir: Path) -> set[str]:
    return {path.name for path in data_dir.iterdir()}


def test_command_writes_public_set_and_fake_data(tmp_path: Path) -> None:
    outcome = CliRunner().invoke(cli, ["fake-data", "--size", "small", "--output", str(tmp_path)])
    assert outcome.exit_code == 0, outcome.output
    assert written_files(tmp_path) == PUBLIC_FILE_NAMES | {FAKE_DATA_FILE_NAME}


def test_first_start_offers_fake_data_outside_production(tmp_path: Path) -> None:
    with CliRunner().isolation(input="medium\n"):
        offer_fake_data(tmp_path, "dev")
    assert "taille medium" in (tmp_path / FAKE_DATA_FILE_NAME).read_text(encoding="utf-8")


def test_own_files_choice_writes_nothing(tmp_path: Path) -> None:
    with CliRunner().isolation(input="none\n\n"):
        offer_fake_data(tmp_path, "dev")
    assert written_files(tmp_path) == set()


def test_production_never_gets_fake_data(tmp_path: Path) -> None:
    with CliRunner().isolation(input="\n"):
        offer_fake_data(tmp_path, "prod")
    assert written_files(tmp_path) == set()
