"""Client HTTP avec cache disque, limitation de débit et retries."""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from pathlib import Path

import requests

log = logging.getLogger("scrape_idu")


class Fetcher:
    def __init__(self, cache_dir: Path, delay: float = 0.3, retries: int = 3):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; learnagement-scraper/1.0; usage interne Polytech)",
                "Accept-Language": "fr-FR,fr;q=0.9",
            }
        )
        self._lock = threading.Lock()
        self._last = 0.0

    def _throttle(self) -> None:
        with self._lock:
            wait = self._last + self.delay - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()

    def get(self, url: str) -> str:
        path = self.cache_dir / (hashlib.sha1(url.encode()).hexdigest() + ".html")
        if path.exists():
            return path.read_text(encoding="utf-8")
        last_exc: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                self._throttle()
                r = self.session.get(url, timeout=30)
                r.raise_for_status()
                r.encoding = "utf-8"
                path.write_text(r.text, encoding="utf-8")
                return r.text
            except requests.RequestException as exc:  # noqa: PERF203
                last_exc = exc
                log.warning("Echec %s (tentative %d/%d) : %s", url, attempt, self.retries, exc)
                time.sleep(1.5 * attempt)
        raise RuntimeError(f"Impossible de recuperer {url}") from last_exc
