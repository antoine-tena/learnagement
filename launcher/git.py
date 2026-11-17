"""Le commit de l'instance, écrit dans `.env.git` (GIT_COMMIT) et tenu à jour par des hooks git.

En ligne de commande, appelé par les hooks : `python launcher/git.py [--short] [--out FICHIER]`.
"""

import argparse
import subprocess
import sys
from pathlib import Path

COMMIT_FILE = ".env.git"
DIRTY_SUFFIX = "-DIRTY"
HOOK_TEMPLATE = """#!/bin/sh
# Hook {hook_name} généré par launcher/git.py : met à jour {commit_file} après {trigger}.
"{python}" "{script}" --out "{commit_file}" {short_flag}|| true
"""
HOOKS = {
    "post-commit": "un commit",
    "post-merge": "un pull/merge",
    "post-rewrite": "un rebase/amend",
}


def _run_git(args: list[str], cwd: Path | None = None) -> str | None:
    """La sortie d'une commande git, ou None si elle échoue."""
    try:
        completed = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return completed.stdout.strip() or None


def get_branch(repo_dir: Path | None = None) -> str | None:
    return _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir)


def get_commit_hash(is_short: bool = False, repo_dir: Path | None = None) -> str | None:
    """Le commit de HEAD, suivi de -DIRTY si la copie de travail a des modifications."""
    args = ["rev-parse", "--short", "HEAD"] if is_short else ["rev-parse", "HEAD"]
    commit = _run_git(args, cwd=repo_dir)
    if commit is None:
        return None
    is_dirty = bool(_run_git(["status", "--porcelain"], cwd=repo_dir))
    return commit + DIRTY_SUFFIX if is_dirty else commit


def write_commit_file(path: str | Path = COMMIT_FILE, is_short: bool = False) -> str | None:
    """Écrit GIT_COMMIT dans `path` ; renvoie le commit écrit, ou None."""
    commit = get_commit_hash(is_short=is_short)
    if commit is not None:
        Path(path).write_text(f"GIT_COMMIT={commit}\n", encoding="utf-8")
    return commit


def _hooks_dir(repo: Path) -> Path:
    """Le dossier des hooks, en respectant core.hooksPath et les worktrees."""
    custom = _run_git(["config", "--get", "core.hooksPath"], cwd=repo)
    hooks = (
        Path(custom)
        if custom
        else Path(_run_git(["rev-parse", "--git-common-dir"], cwd=repo) or ".git") / "hooks"
    )
    return hooks if hooks.is_absolute() else repo / hooks


def install_hooks(repo_dir: str | Path = ".", is_short: bool = True) -> list[Path]:
    """Installe les hooks post-commit, post-merge et post-rewrite ; [] hors d'un dépôt git."""
    repo = Path(repo_dir).resolve()
    if _run_git(["rev-parse", "--git-dir"], cwd=repo) is None:
        return []
    hooks_dir = _hooks_dir(repo)
    hooks_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for hook_name, trigger in HOOKS.items():
        hook_file = hooks_dir / hook_name
        hook_file.write_text(
            HOOK_TEMPLATE.format(
                hook_name=hook_name,
                trigger=trigger,
                python=sys.executable,
                script=Path(__file__).resolve(),
                commit_file=(repo / COMMIT_FILE).resolve(),
                short_flag="--short " if is_short else "",
            ),
            encoding="utf-8",
        )
        hook_file.chmod(0o755)
        written.append(hook_file)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Écrit le commit git courant.")
    parser.add_argument("--short", action="store_true", help="Commit abrégé")
    parser.add_argument("--out", default=COMMIT_FILE, help="Fichier de sortie")
    args = parser.parse_args(argv)
    commit = write_commit_file(path=args.out, is_short=args.short)
    if commit is None:
        print("!! Impossible de lire le commit (pas de dépôt git ?)", file=sys.stderr)
        return 1
    print(commit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
