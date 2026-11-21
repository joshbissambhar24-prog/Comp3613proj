"""Integration wiring: use after Josh, Kyle and Stephen's branches have merged.

Preserves existing API: subscribe, notify, clear_observers, ensure_default_observers,
and inbox. The startup seed uses ensure_default_observers().
"""
from __future__ import annotations
from typing import Any
from sqlmodel import Session, select
from app.database import engine
from app.models.notification import Notification
from app.services.event_bus import DeliveryReport, NotificationEvent, NotificationSubject
from app.services.notification_observer import InAppNotificationObserver

subject = NotificationSubject()
_persistence_observer = InAppNotificationObserver()


def subscribe(observer) -> None:
    subject.subscribe(observer)


def clear_observers() -> None:
    subject.clear()


def ensure_default_observers() -> None:
    subject.subscribe(_persistence_observer)


def notify(event: dict[str, Any]) -> DeliveryReport:
    """Publish one event with explicit recipients (no implicit all-user fan-out)."""
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
