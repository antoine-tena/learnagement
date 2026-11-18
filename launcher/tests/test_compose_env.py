"""La compose assemblée par fragments et les parts de l'environnement, sans docker."""

from pathlib import Path

import pytest
import yaml

from launcher import compose, env
from launcher.config import COMPOSE_FRAGMENTS, CONTAINER_APP_DIRS, CONTAINERS

VARIABLES = {name: "x" for name in compose.COMPOSE_VARIABLES} | {"INSTANCE_NAME": "test"}


@pytest.mark.parametrize("env_name", sorted(CONTAINERS))
def test_each_environment_gets_a_valid_compose(env_name: str) -> None:
    services = yaml.safe_load(compose.render_compose(CONTAINERS[env_name], VARIABLES))["services"]
    assert len(services) == len(CONTAINERS[env_name])
    assert ("front_nextjs_test" in services) is (env_name == "dev")


def test_every_fragment_is_valid_and_known() -> None:
    every_container = sorted(CONTAINER_APP_DIRS)
    rendered = compose.render_compose(every_container, VARIABLES)
    assert len(yaml.safe_load(rendered)["services"]) == len(every_container)


def test_every_container_has_a_fragment() -> None:
    assert sorted(COMPOSE_FRAGMENTS) == sorted(CONTAINER_APP_DIRS)
    assert all(Path(fragment).is_file() for fragment in COMPOSE_FRAGMENTS.values())


def test_passwords_stay_out_of_the_compose_file() -> None:
    rendered = compose.render_compose(CONTAINERS["prod"], VARIABLES)
    assert "${MYSQL_USER_PASSWORD}" in rendered


def test_podman_maps_the_user_into_the_frontend() -> None:
    """Sous podman sans root, `node` est l'utilisateur de la machine : il écrit node_modules."""
    variables = VARIABLES | {"USERNS_MODE": compose.userns_mode("/usr/bin/podman")}
    services = yaml.safe_load(compose.render_compose(CONTAINERS["dev"], variables))["services"]
    assert services["front_nextjs_test"]["userns_mode"] == "keep-id"
    assert compose.userns_mode("docker") == "host"


def test_launcher_waits_as_long_as_the_health_checks() -> None:
    services = yaml.safe_load(compose.render_compose(CONTAINERS["dev"], VARIABLES))["services"]
    for service in services.values():
        check = service.get("healthcheck", {})
        budget = int(check.get("retries", 0)) * int(str(check.get("interval", "0s")).rstrip("s"))
        assert budget <= compose.READY_TIMEOUT_SECONDS


def test_podman_ps_reads_health_from_status() -> None:
    """podman rend un tableau sur plusieurs lignes, sans clé Health."""
    output = (
        '[\n {"State": "running", "Status": "Up 3 minutes (healthy)"},\n'
        ' {"State": "running", "Status": "Up 9 seconds (starting)"},\n'
        ' {"State": "running", "Status": "Up 2 hours"}\n]\n'
    )
    readiness = [compose._is_ready(container) for container in compose.parse_compose_ps(output)]
    assert readiness == [True, False, True]


def test_podman_compose_ps_has_no_all_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCKER_COMPOSE_COMMAND", "podman compose")
    monkeypatch.setenv("COMPOSE_PROJECT_NAME", "learnagement_test")
    assert "--all" not in compose.compose_ps_command(is_podman=True)
    assert "--all" in compose.compose_ps_command(is_podman=False)


def test_compose_ps_accepts_a_list_or_one_object_per_line() -> None:
    as_list = '[{"State": "running"}, {"State": "exited", "ExitCode": 0}]'
    per_line = '{"State": "running"}\n{"State": "exited", "ExitCode": 0}\n'
    assert compose.parse_compose_ps(as_list) == compose.parse_compose_ps(per_line)


def test_env_parts_are_merged(tmp_path: Path) -> None:
    (tmp_path / ".env.default").write_text("INSTANCE_NAME=test\n", encoding="utf-8")
    (tmp_path / ".env.git").write_text("GIT_COMMIT=abc123\n", encoding="utf-8")
    (tmp_path / ".env_dev.env").write_text("ENV=dev\n", encoding="utf-8")
    assert env.load_env_parts(tmp_path) == {"INSTANCE_NAME": "test", "GIT_COMMIT": "abc123"}


def test_a_key_defined_in_two_parts_is_refused(tmp_path: Path) -> None:
    (tmp_path / ".env.default").write_text("GIT_COMMIT=a\n", encoding="utf-8")
    (tmp_path / ".env.git").write_text("GIT_COMMIT=b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="GIT_COMMIT"):
        env.load_env_parts(tmp_path)


def test_next_backup_is_today_or_tomorrow() -> None:
    from datetime import datetime, time

    from launcher.backups.schedule import PARIS, parse_backup_at, seconds_until

    morning = datetime(2026, 11, 17, 8, 0, tzinfo=PARIS)
    assert parse_backup_at("22h30") == time(22, 30)
    assert seconds_until(time(9, 0), morning) == 3600
    assert seconds_until(time(7, 0), morning) == 23 * 3600


def test_production_is_backed_up_with_a_health_check() -> None:
    services = yaml.safe_load(compose.render_compose(CONTAINERS["prod"], VARIABLES))["services"]
    backup = services["data_mysql_backup_test"]
    assert backup["healthcheck"]["test"][-1] == "health"
    assert "${MYSQL_USER_PASSWORD}" in str(backup["environment"])


def test_production_has_no_phpmyadmin() -> None:
    """La base de prod contient des données personnelles : pas d'interface d'administration."""
    assert "phpmyadmin" not in CONTAINERS["prod"]
