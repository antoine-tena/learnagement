"""La commande se charge et annonce ses imports, sans ouvrir de navigateur."""

import pytest
from click.testing import CliRunner

from learnagement_scraping.cli import cli

COMMANDS = ("disciplines", "semestres", "enseignants", "etudiants", "modules", "profil", "notes")


def test_help_lists_every_import() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    for command in (*COMMANDS, "stages"):
        assert command in result.output


@pytest.mark.parametrize("command", COMMANDS)
def test_each_command_has_help(command: str) -> None:
    assert CliRunner().invoke(cli, [command, "--help"]).exit_code == 0
