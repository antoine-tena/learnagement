"""Une sauvegarde, sa rétention et sa planification quotidienne."""

import asyncio
import logging
import os
import re
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import dotenv

from launcher import db
from launcher.backups.remote import env_bool, mounted_remote
from launcher.config import GREEN, NC, RED, YELLOW

logger = logging.getLogger(__name__)

PARIS = ZoneInfo("Europe/Paris")
DEFAULT_BACKUP_DIRECTORY = "db/backup"
DEFAULT_BACKUP_AT = "00:00"
BACKUP_PREFIXES = ("0_struct_", "5_data_", "99_trigger_")
SECONDS_PER_DAY = 86400

_backup_task: asyncio.Task[None] | None = None


def parse_backup_at(value: str | None) -> time:
    value = (value or DEFAULT_BACKUP_AT).strip()
    match = re.fullmatch(r"([01]?\d|2[0-3])[:hH]([0-5]\d)", value)
    if not match:
        raise ValueError(f"BACKUP_AT invalide : '{value}' (format attendu HH:MM)")
    return time(int(match.group(1)), int(match.group(2)))


def seconds_until(at: time, now: datetime) -> float:
    """Le délai jusqu'au prochain `at`, heure de Paris."""
    target = now.replace(hour=at.hour, minute=at.minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def purge_old_backups(folder: Path) -> None:
    days = os.environ.get("BACKUP_RETENTION_DAYS", "").strip()
    if not days:
        return
    try:
        limit = datetime.now(PARIS).timestamp() - int(days) * SECONDS_PER_DAY
    except ValueError:
        logger.warning("%sBACKUP_RETENTION_DAYS invalide : '%s', purge ignorée%s", YELLOW, days, NC)
        return
    for backup_file in folder.glob("*.sql"):
        if backup_file.name.startswith(BACKUP_PREFIXES) and backup_file.stat().st_mtime < limit:
            backup_file.unlink(missing_ok=True)
            logger.info("Old backup removed: %s", backup_file.name)


def run_backup_once() -> None:
    """Une sauvegarde complète : sur le partage distant (monté puis démonté) ou en local."""
    dotenv.load_dotenv()
    remote = os.environ.get("BACKUP_REMOTE_DIRECTORY", "").strip()
    if remote:
        with mounted_remote(remote) as mount_path:
            db.backup(mount_path)
            purge_old_backups(mount_path)
        return
    local = Path(os.environ.get("BACKUP_DIRECTORY", "").strip() or DEFAULT_BACKUP_DIRECTORY)
    db.backup(local)
    purge_old_backups(local)


async def _backup_loop(at: time) -> None:
    while True:
        delay = seconds_until(at, datetime.now(PARIS))
        next_run = datetime.now(PARIS) + timedelta(seconds=delay)
        logger.info("%sNext DB backup: %s%s", GREEN, f"{next_run:%Y-%m-%d %H:%M}", NC)
        await asyncio.sleep(delay)
        try:
            await asyncio.to_thread(run_backup_once)  # subprocess et montages sont bloquants
        except asyncio.CancelledError:
            raise
        except Exception:  # une sauvegarde ratée ne doit jamais arrêter l'application
            logger.exception("%sDB backup failed%s", RED, NC)


async def launch_backup_system() -> asyncio.Task[None] | None:
    """Lance en tâche de fond la sauvegarde quotidienne si BACKUP est vrai, sans attendre."""
    global _backup_task
    dotenv.load_dotenv()
    if not env_bool("BACKUP"):
        logger.info("DB backup system disabled (BACKUP is not set to true)")
        return None
    try:
        at = parse_backup_at(os.environ.get("BACKUP_AT"))
    except ValueError:
        logger.exception("%sBackup system not started%s", RED, NC)
        return None
    if _backup_task is None or _backup_task.done():
        _backup_task = asyncio.create_task(_backup_loop(at), name="learnagement-db-backup")
        logger.info("%sDB backup system started (every day at %s)%s", GREEN, f"{at:%H:%M}", NC)
    return _backup_task
