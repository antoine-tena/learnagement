"""Journalisation structurée de l'API : des événements `domaine.evenement` et leurs champs."""

import copy
import logging
import os
from typing import Any, override

import structlog
from uvicorn.config import LOGGING_CONFIG

HEALTH_PATH = "/health"
PROD_ENV = "prod"


class HealthFilter(logging.Filter):
    """Écarte du journal d'accès d'uvicorn les appels de la sonde de santé."""

    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return HEALTH_PATH not in record.getMessage()


def _is_prod() -> bool:
    return os.getenv("ENV", "dev") == PROD_ENV


def configure_logging() -> None:
    """Configure structlog : JSON en production, lisible en console ailleurs."""
    renderer: Any = (
        structlog.processors.JSONRenderer() if _is_prod() else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.CallsiteParameterAdder(
                [structlog.processors.CallsiteParameter.MODULE]
            ),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


def uvicorn_log_config() -> dict[str, Any]:
    """Configuration des journaux d'uvicorn, sans les appels de la sonde de santé."""
    log_config = copy.deepcopy(LOGGING_CONFIG)
    log_config.setdefault("filters", {})["skip_health"] = {"()": HealthFilter}
    log_config["handlers"]["access"]["filters"] = ["skip_health"]
    return log_config


configure_logging()
logger = structlog.get_logger()
