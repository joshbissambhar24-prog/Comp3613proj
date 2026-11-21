"""Kyle: in-app persistence Observer (Sprint 2 task #12).

Uses the existing Notification table without a schema migration. The source
key is part of the stored message to distinguish two campaigns with same text.
The database should ultimately enforce uniqueness for concurrent delivery.
"""
from __future__ import annotations

from datetime import datetime, timezone
from sqlmodel import Session, select
from app.database import engine
from app.models.notification import Notification
from app.services.event_bus import NotificationEvent


class InAppNotificationObserver:
    def __call__(self, event: NotificationEvent) -> None:
        message = f"[{event.source_key}] {event.message}"
        with Session(engine) as session:
            for user_id in dict.fromkeys(event.recipient_ids):
                existing = session.exec(
                    select(Notification).where(
                        Notification.user_id == user_id,
                        Notification.event_type == event.event_type,
                        Notification.message == message,
                    )
                ).first()
                if existing is not None:
                    continue
                session.add(Notification(
                    user_id=user_id,
                    event_type=event.event_type,
                    message=message,
                    created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                ))
            session.commit()
