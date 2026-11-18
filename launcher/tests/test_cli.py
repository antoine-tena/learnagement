"""Le lanceur, sans docker : les commandes externes sont simulées."""

import asyncio
import subprocess
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from launcher import cli as cli_module
from launcher import db, docker


def test_docker_option_becomes_arguments() -> None:
    assert docker.parse_docker_options("-d --wait") == ["-d", "--wait"]
    assert docker.parse_docker_options(None) == []


def test_command_names_stay_stable() -> None:
    assert set(cli_module.cli.commands) == {
        "backupdb",
        "exportinstance",
        "fake-data",
        "generate-env",
        "gui",
        "import-instance",
        "start",
        "stop",
        "structuredb",
    }


def test_start_passes_docker_option_as_a_list(monkeypatch: pytest.MonkeyPatch) -> None:
    received: list[list[str]] = []
    monkeypatch.setattr(cli_module, "_start", received.append)
    result = CliRunner().invoke(cli_module.cli, ["start", "--docker_option=-d", "--rebuild"])
    assert result.exit_code == 0, result.output
    assert received == [["--build", "-d"]]


def test_administrator_is_prepared_while_compose_stays_in_foreground(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def scenario() -> list[str]:
        events: list[str] = []
        loop = asyncio.get_running_loop()
        release = asyncio.Event()

        def compose_up(_options: list[str]) -> None:
            events.append("up")
            asyncio.run_coroutine_threadsafe(release.wait(), loop).result(timeout=5)
            events.append("down")

        async def setup() -> None:
            events.append("administrator")
            release.set()

        monkeypatch.setattr(docker, "compose_up", compose_up)
        monkeypatch.setattr(cli_module, "_setup_administrator", setup)
        await cli_module._run_instance([])
        return events

    events = asyncio.run(scenario())
    assert events.index("administrator") < events.index("down")


def test_compose_failure_stops_the_wait_for_mysql(monkeypatch: pytest.MonkeyPatch) -> None:
    def compose_up(_options: list[str]) -> None:
        raise subprocess.CalledProcessError(1, "up")

    async def setup() -> None:
        await asyncio.sleep(60)

    monkeypatch.setattr(docker, "compose_up", compose_up)
    monkeypatch.setattr(cli_module, "_setup_administrator", setup)
    with pytest.raises(subprocess.CalledProcessError):
        asyncio.run(asyncio.wait_for(cli_module._run_instance([]), timeout=5))


def test_backup_keeps_the_password_out_of_the_arguments(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    secret = "not-a-real-password"
    monkeypatch.setenv("DOCKER_COMMAND", "docker")
    monkeypatch.setenv("MYSQL_SERVER", "learnagement_data_mysql_test")
    monkeypatch.setenv("MYSQL_USER_LOGIN", "user")
    monkeypatch.setenv("MYSQL_USER_PASSWORD", secret)
    monkeypatch.setenv("MYSQL_DB", "learnagement")
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def fake_run(command: list[str], **kwargs: Any) -> None:
        calls.append((command, kwargs))

    monkeypatch.setattr(subprocess, "run", fake_run)
    db.backup(tmp_path)

    dumps = [call for call in calls if "mysqldump" in call[0]]
    assert len(dumps) == 3
    for command, kwargs in dumps:
        assert not any(secret in argument for argument in command)
        assert kwargs["env"]["MYSQL_PWD"] == secret
    assert len(list(tmp_path.glob("*.sql"))) == 3


def test_structure_keeps_views_routines_and_triggers_without_data(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("DOCKER_COMMAND", "docker")
    monkeypatch.setenv("MYSQL_SERVER", "learnagement_data_mysql_test")
    monkeypatch.setenv("MYSQL_USER_LOGIN", "user")
    monkeypatch.setenv("MYSQL_USER_PASSWORD", "not-a-real-password")
    monkeypatch.setenv("MYSQL_ROOT_PASSWORD", "not-a-real-root-password")
    monkeypatch.setenv("MYSQL_DB", "learnagement")
    commands: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> None:
        commands.append(command)
        assert kwargs["env"]["MYSQL_PWD"] == "not-a-real-root-password"
        kwargs["stdout"].write(b"CREATE TABLE t (c INT COMMENT 'sens');")

    monkeypatch.setattr(subprocess, "run", fake_run)
    target = tmp_path / "structure.sql"
    db.extract_structure(target)

    (command,) = commands
    assert command[command.index("-u") + 1] == "root"
    assert "--no-data" in command
    assert "--routines" in command
    assert "--ignore-views" not in command
    assert "--skip-triggers" not in command
    assert "COMMENT 'sens'" in target.read_text()


def test_structuredb_writes_to_the_given_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    received: list[Path] = []
    monkeypatch.setattr(db, "extract_structure", received.append)
    target = tmp_path / "s.sql"
    result = CliRunner().invoke(cli_module.cli, ["structuredb", "--output", str(target)])
    assert result.exit_code == 0, result.output
    assert received == [target]


def test_gui_explains_the_missing_dependency() -> None:
    result = CliRunner().invoke(cli_module.cli, ["gui"])
    assert result.exit_code == 1
    assert "click-gui-runner" in result.output
