"""Sprint 2 Task #18: API-to-service-to-Observer integration tests for UWI Connect.

Copy this file to tests/test_sprint2_workflows.py in the project.
Requires the existing tests/conftest.py test_session fixture.
The tests use an isolated in-memory SQLite database, not the development database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from app.main import app
from app.models.campaign import Campaign
from app.models.notification import Notification
from app.models.user import User
from app.services.event_bus import NotificationSubject
from app.services.notification_observer import InAppNotificationObserver
from app.services.retry_observer import RetryObserver


@pytest.fixture
def scenario_client(test_session, monkeypatch):
    """Use the real API/services/Observer with isolated test storage."""
    from app.services import accounts, board_auth, boards, campaigns, notification_observer
    from app.services import notifications, recipient_policy

    # Each service imports the engine by name, so patch each reference.
    for module in (
        accounts,
        board_auth,
        boards,
        campaigns,
        notification_observer,
        notifications,
        recipient_policy,
    ):
        monkeypatch.setattr(module, "engine", test_session.bind)

    # Keep the global Observer registry isolated between test cases.
    monkeypatch.setattr(notifications, "subject", NotificationSubject())
    monkeypatch.setattr(
        notifications,
        "_persistence_observer",
        RetryObserver(InAppNotificationObserver(), max_attempts=3),
    )

    users = (
        (1, "admin", 1),
        (2, "alumni", 1),
        (3, "alumni", 0),
        (4, "alumni", 1),
    )
    for user_id, role, verified in users:
        test_session.add(
            User(
                id=user_id,
                username=f"sprint2user{user_id}",
                email=f"sprint2user{user_id}@example.com",
                password="test-only-not-for-login",
                role=role,
                email_verified=verified,
                display_name=f"User {user_id}",
            )
        )
    test_session.commit()

    # Do not enter TestClient's lifespan context: it seeds the development DB.
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()


def headers(user_id):
    return {"x-user-id": str(user_id)}


def inbox(client, user_id):
    response = client.get("/api/notifications", headers=headers(user_id))
    assert response.status_code == 200, response.text
    return response.json()["notifications"]


@pytest.mark.parametrize("kind", ["job", "event"])
def test_listing_approval_creates_verified_only_notifications(scenario_client, kind):
    client = scenario_client

    submitted = client.post(
        "/api/boards/listings",
        headers=headers(2),
        json={"kind": kind, "title": f"Graduate {kind}", "body": "Sprint 2 integration test"},
    )
    assert submitted.status_code == 200, submitted.text
    listing = submitted.json()["listing"]
    assert listing["status"] == "pending"
    listing_id = listing["id"]

    # Before approval, the listing is not public and nobody was notified.
    visible = client.get("/api/boards")
    assert visible.status_code == 200
    assert all(row["id"] != listing_id for row in visible.json()["listings"])
    assert inbox(client, 2) == []

    published = client.post(
        f"/api/admin/listings/{listing_id}/publish", headers=headers(1)
    )
    assert published.status_code == 200, published.text
    assert published.json()["listing"]["status"] == "published"
    assert published.json()["notified"] is True
    assert published.json()["notification_failures"] == 0

    visible = client.get("/api/boards")
    assert any(row["id"] == listing_id for row in visible.json()["listings"])

    # Both verified alumni receive exactly one notification; others receive none.
    for user_id in (2, 4):
        messages = inbox(client, user_id)
        assert len(messages) == 1
        assert messages[0]["event_type"] == "listing.published"
        assert f"[listing:{listing_id}]" in messages[0]["message"]
    assert inbox(client, 3) == []  # unverified alumnus
    assert inbox(client, 1) == []  # administrator

    # Publishing again must fail instead of dispatching duplicate notifications.
    repeated = client.post(
        f"/api/admin/listings/{listing_id}/publish", headers=headers(1)
    )
    assert repeated.status_code == 400
    assert len(inbox(client, 2)) == 1


def test_campaign_send_creates_verified_only_notifications(scenario_client):
    client = scenario_client
    created = client.post(
        "/api/admin/campaigns",
        headers=headers(1),
        json={"subject": "Alumni careers", "body": "New graduate opportunities."},
    )
    assert created.status_code == 200, created.text
    campaign = created.json()["campaign"]
    assert campaign["status"] == "draft"
    campaign_id = campaign["id"]
    assert inbox(client, 2) == []

    sent = client.post(
        f"/api/admin/campaigns/{campaign_id}/send", headers=headers(1)
    )
    assert sent.status_code == 200, sent.text
    assert sent.json()["campaign"]["status"] == "sent"
    assert sent.json()["notification_failures"] == 0

    for user_id in (2, 4):
        messages = inbox(client, user_id)
        assert len(messages) == 1
        assert messages[0]["event_type"] == "campaign.sent"
        assert f"[campaign:{campaign_id}]" in messages[0]["message"]
    assert inbox(client, 3) == []
    assert inbox(client, 1) == []

    repeated = client.post(
        f"/api/admin/campaigns/{campaign_id}/send", headers=headers(1)
    )
    assert repeated.status_code == 400
    assert len(inbox(client, 2)) == 1


def test_rejected_listing_is_not_published_or_notified(scenario_client):
    client = scenario_client
    created = client.post(
        "/api/boards/listings",
        headers=headers(2),
        json={"kind": "job", "title": "Rejected posting", "body": "Not approved"},
    )
    listing_id = created.json()["listing"]["id"]
    rejected = client.post(
        f"/api/admin/listings/{listing_id}/reject", headers=headers(1)
    )
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["listing"]["status"] == "rejected"
    assert all(
        row["id"] != listing_id
        for row in client.get("/api/boards").json()["listings"]
    )
    assert inbox(client, 2) == []
    assert inbox(client, 4) == []


def test_unverified_cannot_submit_and_alumnus_cannot_publish(scenario_client):
    client = scenario_client
    denied = client.post(
        "/api/boards/listings",
        headers=headers(3),
        json={"kind": "job", "title": "Unverified", "body": "Denied"},
    )
    assert denied.status_code == 400

    created = client.post(
        "/api/boards/listings",
        headers=headers(2),
        json={"kind": "job", "title": "Admin approval needed", "body": "Pending"},
    )
    assert created.status_code == 200
    listing_id = created.json()["listing"]["id"]
    not_admin = client.post(
        f"/api/admin/listings/{listing_id}/publish", headers=headers(2)
    )
    assert not_admin.status_code == 400
    assert inbox(client, 2) == []



def test_verification_changes_eligibility_for_future_campaign(scenario_client):
    """Exercise the current demo verification endpoint and audience selection."""
    client = scenario_client
    assert inbox(client, 3) == []
    verified = client.post("/api/auth/verify-email", headers=headers(3))
    assert verified.status_code == 200, verified.text
    assert verified.json()["user"]["email_verified"] == 1

    created = client.post(
        "/api/admin/campaigns",
        headers=headers(1),
        json={"subject": "Welcome verified alumni", "body": "You are now eligible."},
    )
    campaign_id = created.json()["campaign"]["id"]
    sent = client.post(
        f"/api/admin/campaigns/{campaign_id}/send", headers=headers(1)
    )
    assert sent.status_code == 200
    assert sent.json()["notification_failures"] == 0
    notifications = inbox(client, 3)
    assert len(notifications) == 1
    assert notifications[0]["event_type"] == "campaign.sent"

    # Caution: the current verify-email endpoint is a demo stub, not secure
    # token-based ownership verification. This checks its actual behaviour.


def test_campaign_observer_failure_is_reported(scenario_client, monkeypatch, test_session):
    """Simulate a persistence outage; verify API -> Observer -> failure report."""
    from app.services.notification_observer import InAppNotificationObserver

    def broken_persistence(self, event):
        raise RuntimeError("simulated temporary database outage")

    monkeypatch.setattr(InAppNotificationObserver, "__call__", broken_persistence)
    client = scenario_client
    created = client.post(
        "/api/admin/campaigns",
        headers=headers(1),
        json={"subject": "Failure simulation", "body": "Delivery diagnostic"},
    )
    assert created.status_code == 200
    campaign_id = created.json()["campaign"]["id"]

    sent = client.post(
        f"/api/admin/campaigns/{campaign_id}/send", headers=headers(1)
    )
    assert sent.status_code == 200, sent.text
    assert sent.json()["notification_failures"] == 1
    from app.services.notifications import recent_persistence_attempts
    assert recent_persistence_attempts()[-1].attempts == 3
    assert recent_persistence_attempts()[-1].delivered is False
    assert inbox(client, 2) == []
    assert inbox(client, 4) == []

    # The current code records the campaign as sent even if notification fails;
    # this test documents that limitation rather than claiming successful delivery.
    stored = test_session.get(Campaign, campaign_id)
    assert stored.status == "sent"
    assert test_session.exec(select(Notification)).all() == []


def test_non_admin_cannot_manage_campaigns(scenario_client):
    """Campaign creation and sending must require administrator privileges."""
    client = scenario_client
    denied = client.post(
        "/api/admin/campaigns",
        headers=headers(2),
        json={"subject": "Not allowed", "body": "Only admins can send campaigns"},
    )
    assert denied.status_code == 400

    created = client.post(
        "/api/admin/campaigns",
        headers=headers(1),
        json={"subject": "Approved", "body": "Admin created this"},
    )
    assert created.status_code == 200
    campaign_id = created.json()["campaign"]["id"]

    denied_send = client.post(
        f"/api/admin/campaigns/{campaign_id}/send", headers=headers(2)
    )
    assert denied_send.status_code == 400
    assert inbox(client, 2) == []


def test_shared_observer_is_idempotent_for_same_source_event(scenario_client):
    """Re-dispatching one source/event must not duplicate notification rows."""
    from app.services import notifications

    event = {
        "event_type": "campaign.sent",
        "source_key": "campaign:integration-idempotency",
        "recipient_ids": (2, 2, 4),
        "message": "Careers update",
    }
    assert notifications.notify(event).failed == 0
    assert notifications.notify(event).failed == 0

    for user_id in (2, 4):
        rows = inbox(scenario_client, user_id)
        assert len(rows) == 1
        assert rows[0]["event_type"] == "campaign.sent"
    assert inbox(scenario_client, 3) == []
