"""Retryable Observer adapter for the UWI Connect notification pipeline.

Retries are synchronous and bounded. A final failure is re-raised so the
NotificationSubject can isolate it and count it in the DeliveryReport.
The in-memory attempt history is diagnostics only, not persistent delivery
tracking; durable status tracking would require a database model/migration.
"""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from typing import Callable

from app.services.event_bus import NotificationEvent

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AttemptRecord:
    source_key: str
    event_type: str
    attempts: int
    delivered: bool
    last_error: str | None = None


class RetryObserver:
    """Decorate an Observer with a finite number of delivery attempts.

    ``max_attempts`` includes the initial attempt; three means one initial
    attempt plus at most two retries. There is no sleep, so this is intended
    for transient errors in short in-process operations, not email services.
    """

    def __init__(
        self,
        observer: Callable[[NotificationEvent], None],
        *,
        max_attempts: int = 3,
        history_limit: int = 100,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if history_limit < 1:
            raise ValueError("history_limit must be at least 1")
        self.observer = observer
        self.max_attempts = max_attempts
        self._history: deque[AttemptRecord] = deque(maxlen=history_limit)

    @property
    def history(self) -> tuple[AttemptRecord, ...]:
        """Recent results, oldest first. This is not durable storage."""
        return tuple(self._history)

    def __call__(self, event: NotificationEvent) -> None:
        for attempt in range(1, self.max_attempts + 1):
            try:
                self.observer(event)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                logger.warning(
                    "Observer delivery attempt %d/%d failed for %s: %s",
                    attempt, self.max_attempts, event.source_key, error,
                )
                if attempt == self.max_attempts:
                    self._history.append(AttemptRecord(
                        event.source_key, event.event_type, attempt, False, error,
                    ))
                    raise
            else:
                self._history.append(AttemptRecord(
                    event.source_key, event.event_type, attempt, True,
                ))
                return
