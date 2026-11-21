"""Stephen: event/job approval, one-time publication and audience policy."""
from types import SimpleNamespace
from sqlmodel import select
from app.models.listing import Listing
from app.models.user import User


def test_listing_submission_stays_pending(test_session, monkeypatch):
    import app.services.boards as boards
    monkeypatch.setattr(boards, "engine", test_session.bind)
    monkeypatch.setattr(boards, "get_user", lambda uid: {"role": "alumni", "email_verified": 1})
    result = boards.submit_listing(5, kind="event", title="Open Day", body="Campus")
    assert result["ok"]
    assert result["listing"]["status"] == "pending"
    assert boards.browse_published(kind="event") == []


def test_publish_once_and_notify_for_a_job(test_session, monkeypatch):
    import app.services.boards as boards
    monkeypatch.setattr(boards, "engine", test_session.bind)
    monkeypatch.setattr(boards, "get_user", lambda uid: {"role": "admin"})
    monkeypatch.setattr(boards, "verified_alumni_ids", lambda: (2, 4))
    events = []
    monkeypatch.setattr(boards.notifications, "notify", lambda event: (events.append(event), SimpleNamespace(failed=0))[1])
    row = Listing(author_id=2, kind="job", title="Developer", body="Graduate role", status="pending", created_at="2026-11-21")
    test_session.add(row)
    test_session.commit()
    test_session.refresh(row)
    first = boards.publish_listing(1, row.id)
    second = boards.publish_listing(1, row.id)
    assert first["ok"] and first["notified"]
    assert not second["ok"]
    assert len(events) == 1
    assert events[0]["recipient_ids"] == (2, 4)


def test_audience_excludes_unverified_and_admin(test_session, monkeypatch):
    import app.services.recipient_policy as policy
    monkeypatch.setattr(policy, "engine", test_session.bind)
    for uid, role, verified in [(1, "alumni", 1), (2, "alumni", 0), (3, "admin", 1)]:
        test_session.add(User(id=uid, username=f"person{uid}", email=f"person{uid}@my.uwi.edu",
                              password="x", role=role, email_verified=verified))
    test_session.commit()
    assert policy.verified_alumni_ids() == (1,)
