"""Shared Observer wiring for listing publication and campaign sends.

The persistence observer is wrapped in a bounded retry adapter. The public
API (subscribe, notify, clear_observers, inbox) is retained for existing code.
"""
from __future__ import annotations
from typing import Any

from sqlmodel import Session, select
from app.database import engine
from app.models.notification import Notification
from app.services.event_bus import DeliveryReport, NotificationEvent, NotificationSubject
from app.services.notification_observer import InAppNotificationObserver
from app.services.retry_observer import RetryObserver

subject = NotificationSubject()
_persistence_observer = RetryObserver(InAppNotificationObserver(), max_attempts=3)


def subscribe(observer) -> None:
    subject.subscribe(observer)


def clear_observers() -> None:
    subject.clear()


def ensure_default_observers() -> None:
    subject.subscribe(_persistence_observer)


def recent_persistence_attempts():
    """Diagnostic records for the in-app observer since this process started."""
    return _persistence_observer.history


def notify(event: dict[str, Any]) -> DeliveryReport:
    """Dispatch a deduplicated recipient event through registered observers."""
    if "source_key" not in event or "recipient_ids" not in event:
        raise ValueError("Notification event requires source_key and recipient_ids")
    ensure_default_observers()
    typed = NotificationEvent(
        event_type=event["event_type"],
        message=event["message"],
        source_key=event["source_key"],
        recipient_ids=tuple(dict.fromkeys(event["recipient_ids"])),
        metadata={key: value for key, value in event.items()
                  if key not in {"event_type", "message", "source_key", "recipient_ids"}},
    )
    return subject.publish(typed)


def inbox(user_id: int) -> list[dict[str, Any]]:
    with Session(engine) as session:
        rows = session.exec(
            select(Notification).where(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
        ).all()
        return [row.model_dump() for row in rows]
