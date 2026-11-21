"""Josh: tests for subscription, deduplication and observer isolation."""
from app.services.event_bus import NotificationEvent, NotificationSubject


def test_subscribe_once_and_unsubscribe():
    bus = NotificationSubject()
    received = []
    def collect(event):
        received.append(event.source_key)
    bus.subscribe(collect)
    bus.subscribe(collect)
    event = NotificationEvent("campaign.sent", "Hi", "campaign:1", (3,))
    assert bus.publish(event).attempted == 1
    assert received == ["campaign:1"]
    bus.unsubscribe(collect)
    assert bus.publish(event).attempted == 0


def test_one_failed_observer_does_not_block_the_next():
    bus = NotificationSubject()
    received = []
    def broken(event):
        raise ValueError("delivery failed")
    bus.subscribe(broken)
    bus.subscribe(lambda event: received.append(event.message))
    result = bus.publish(NotificationEvent("listing.published", "Live", "listing:2", (1,)))
    assert result.attempted == 2
    assert result.failed == 1
    assert "ValueError" in result.errors[0]
    assert received == ["Live"]
