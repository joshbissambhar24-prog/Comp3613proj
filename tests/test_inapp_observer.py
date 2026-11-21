"""Kyle: in-app persistence and sequential idempotency tests."""
from app.models.notification import Notification
from app.services.event_bus import NotificationEvent
from app.services.notification_observer import InAppNotificationObserver
from sqlmodel import select


def test_notification_saved_once_per_recipient(test_session, monkeypatch):
    import app.services.notification_observer as module
    monkeypatch.setattr(module, "engine", test_session.bind)
    event = NotificationEvent(
        "campaign.sent", "Welcome back", "campaign:101", (1, 1, 2)
    )
    observer = InAppNotificationObserver()
    observer(event)
    observer(event)
    rows = test_session.exec(select(Notification)).all()
    assert len(rows) == 2
    assert {row.user_id for row in rows} == {1, 2}
    assert all("[campaign:101]" in row.message for row in rows)


def test_two_campaigns_with_same_text_are_different(test_session, monkeypatch):
    import app.services.notification_observer as module
    monkeypatch.setattr(module, "engine", test_session.bind)
    observer = InAppNotificationObserver()
    observer(NotificationEvent("campaign.sent", "Hello", "campaign:3", (9,)))
    observer(NotificationEvent("campaign.sent", "Hello", "campaign:4", (9,)))
    rows = test_session.exec(select(Notification)).all()
    assert len(rows) == 2
