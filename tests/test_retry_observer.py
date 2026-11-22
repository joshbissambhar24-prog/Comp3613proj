"""Josh: retry adapter behavior and Observer failure isolation tests."""

import pytest

from app.services.event_bus import NotificationEvent, NotificationSubject
from app.services.retry_observer import RetryObserver


def event():
    return NotificationEvent("campaign.sent", "Welcome", "campaign:42", (5,))


def test_retry_recovers_from_transient_error():
    calls = []

    def flaky(notification):
        calls.append(notification.source_key)
        if len(calls) < 3:
            raise ConnectionError("temporarily unavailable")

    adapter = RetryObserver(flaky, max_attempts=3)
    adapter(event())
    assert len(calls) == 3
    assert adapter.history[-1].delivered is True
    assert adapter.history[-1].attempts == 3


def test_permanent_error_is_reported_and_other_observers_continue():
    calls = []

    def broken(notification):
        calls.append("failed")
        raise RuntimeError("database unavailable")

    adapter = RetryObserver(broken, max_attempts=2)
    bus = NotificationSubject()
    bus.subscribe(adapter)
    bus.subscribe(lambda notification: calls.append("received"))

    report = bus.publish(event())
    assert report.attempted == 2
    assert report.failed == 1
    assert calls == ["failed", "failed", "received"]
    assert adapter.history[-1].delivered is False
    assert adapter.history[-1].attempts == 2
    assert "RuntimeError" in adapter.history[-1].last_error


def test_successful_observer_is_called_only_once():
    calls = []
    adapter = RetryObserver(lambda notification: calls.append(notification), max_attempts=3)
    adapter(event())
    assert len(calls) == 1
    assert adapter.history[-1].attempts == 1


def test_invalid_retry_configuration_rejected():
    with pytest.raises(ValueError):
        RetryObserver(lambda _: None, max_attempts=0)
    with pytest.raises(ValueError):
        RetryObserver(lambda _: None, history_limit=0)


def test_history_is_bounded():
    adapter = RetryObserver(lambda _: None, history_limit=2)
    for n in range(3):
        adapter(NotificationEvent("listing.published", "Live", f"listing:{n}", (5,)))
    assert [entry.source_key for entry in adapter.history] == ["listing:1", "listing:2"]
