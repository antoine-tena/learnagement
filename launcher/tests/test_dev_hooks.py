"""Les hooks de pré-commit installés par bootstrap.py, sans rien installer."""

from pathlib import Path

import pytest

from launcher import dev_hooks


@pytest.mark.parametrize(
    ("content", "expected"),
    [("ENV=prod\n", True), ('ENV="prod"\n', True), ("ENV=dev\n", False), ("", False)],
)
def test_production_is_read_in_env_file(tmp_path: Path, content: str, expected: bool) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(content, encoding="utf-8")
    assert dev_hooks.is_production(env_file) is expected


def test_no_env_file_is_not_production(tmp_path: Path) -> None:
    assert dev_hooks.is_production(tmp_path / ".env") is False


def test_nothing_is_installed_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dev_hooks, "is_production", lambda: True)
    monkeypatch.setattr(dev_hooks.subprocess, "call", pytest.fail)
    assert "production" in dev_hooks.install_dev_hooks("uv")


def test_missing_tools_are_installed_with_uv(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(dev_hooks, "is_production", lambda: False)
    monkeypatch.setattr(dev_hooks.shutil, "which", lambda tool: None if tool == "charter" else tool)
    monkeypatch.setattr(
        dev_hooks.subprocess, "call", lambda command, **_: calls.append(command) or 0
    )
    assert dev_hooks.install_dev_hooks("uv") == "hooks de pré-commit installés"
    assert calls == [["uv", "tool", "install", "ion-repo"], ["pre-commit", "install"]]
