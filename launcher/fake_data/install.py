"""Poser le jeu fictif dans `db/data`, et le proposer au premier lancement hors production."""

import shutil
from pathlib import Path

import click

from launcher.fake_data.generator import (
    DEFAULT_SEED,
    FAKE_DATA_FILE_NAME,
    FakeDataSize,
    generate,
)
from launcher.fake_data.public_set import PUBLIC_SET_DIR

PRODUCTION_ENV = "prod"
OWN_FILES_CHOICE = "none"


def write_fake_data(data_dir: Path, size: FakeDataSize, seed: int = DEFAULT_SEED) -> Path:
    """Copie le jeu public dans `data_dir`, puis y écrit le jeu fictif ; rend son chemin."""
    data_dir.mkdir(parents=True, exist_ok=True)
    for public_file in sorted(PUBLIC_SET_DIR.glob("V*.sql")):
        shutil.copy(public_file, data_dir / public_file.name)
    fake_file = data_dir / FAKE_DATA_FILE_NAME
    fake_file.write_text(generate(size, seed), encoding="utf-8")
    return fake_file


def offer_fake_data(data_dir: Path, env: str) -> None:
    """Au premier lancement, propose un jeu fictif ; la production n'en reçoit jamais."""
    if env != PRODUCTION_ENV:
        choice = click.prompt(
            "Initial data: a size of fictitious people on the public curricula, "
            f"or '{OWN_FILES_CHOICE}' to bring your own files",
            type=click.Choice([*(size.value for size in FakeDataSize), OWN_FILES_CHOICE]),
            default=FakeDataSize.SMALL.value,
        )
        if choice != OWN_FILES_CHOICE:
            fake_file = write_fake_data(data_dir, FakeDataSize(choice))
            click.echo(f"Fictitious data written to '{fake_file}'; test accounts: see README.")
            return
    click.echo(
        f"If you want an initial data set, put it into '{data_dir}' folder "
        "with name matches with V[0-9]*.sql."
    )
    click.echo("Free data samples are available at 'db/freeData' folder.")
    click.prompt("Then press enter", default="", show_default=False)
