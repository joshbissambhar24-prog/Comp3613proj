"""Observer core for UWI Connect. Owned by Josh (Sprint 2 task #11).

A Subject publishes immutable events to independent Observers. Each event
contains explicit recipient IDs so recipient filtering is not hidden in storage.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NotificationEvent:
    event_type: str
    message: str
    source_key: str
    recipient_ids: tuple[int, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


Observer = Callable[[NotificationEvent], None]


@dataclass(frozen=True)
class DeliveryReport:
    attempted: int
    failed: int
    errors: tuple[str, ...]


class NotificationSubject:
    """Subscribe once, publish to every observer even if one fails."""

    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def clear(self) -> None:
        self._observers.clear()

    def publish(self, event: NotificationEvent) -> DeliveryReport:
        errors: list[str] = []
        for observer in tuple(self._observers):
            try:
                observer(event)
            except Exception as exc:
                message = f"{type(observer).__name__}: {type(exc).__name__}: {exc}"
                logger.exception("Notification observer failed for %s", event.source_key)
                errors.append(message)
        return DeliveryReport(attempted=len(self._observers), failed=len(errors), errors=tuple(errors))
