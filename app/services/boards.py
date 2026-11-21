"""Job/event board submission and publication with admin approval.
Stephen owns Sprint 2 task #13; event publications use shared Observer bus.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from sqlmodel import Session, select
from app.database import engine
from app.models.listing import Listing
from app.services import notifications
from app.services.accounts import require_verified_alumni
from app.services.board_auth import get_user
from app.services.recipient_policy import verified_alumni_ids


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def browse_published(*, kind: str | None = None) -> list[dict[str, Any]]:
    with Session(engine) as session:
        stmt = select(Listing).where(Listing.status == "published")
        if kind:
            stmt = stmt.where(Listing.kind == kind)
        stmt = stmt.order_by(Listing.id.desc())
        return [row.model_dump() for row in session.exec(stmt).all()]


def submit_listing(author_id: int, *, kind: str, title: str, body: str) -> dict[str, Any]:
    user = get_user(author_id)
    err = require_verified_alumni(user)
    if user and user["role"] == "admin":
        err = None
    if err:
        return {"ok": False, "error": err}
    if kind not in {"job", "event"}:
        return {"ok": False, "error": "kind must be job|event"}
    with Session(engine) as session:
        listing = Listing(author_id=author_id, kind=kind, title=title, body=body,
                          status="pending", created_at=_now())
        session.add(listing)
        session.commit()
        session.refresh(listing)
        return {"ok": True, "listing": listing.model_dump()}


def list_pending() -> list[dict[str, Any]]:
    with Session(engine) as session:
        return [row.model_dump() for row in session.exec(
            select(Listing).where(Listing.status == "pending").order_by(Listing.id)
        ).all()]


def publish_listing(admin_id: int, listing_id: int) -> dict[str, Any]:
    user = get_user(admin_id)
    if not user or user["role"] != "admin":
        return {"ok": False, "error": "admin only"}
    with Session(engine) as session:
        listing = session.get(Listing, listing_id)
        if listing is None:
            return {"ok": False, "error": "listing not found"}
        if listing.status != "pending":
            return {"ok": False, "error": "listing is not pending"}
        listing.status = "published"
        session.add(listing)
        session.commit()
        session.refresh(listing)
        row = listing.model_dump()

    report = notifications.notify({
        "event_type": "listing.published",
        "source_key": f"listing:{listing_id}",
        "recipient_ids": verified_alumni_ids(),
        "listing_id": listing_id,
        "kind": row["kind"],
        "message": f"New {row['kind']} on the board: {row['title']}",
    })
    return {"ok": True, "listing": row, "notified": report.failed == 0,
            "notification_failures": report.failed}


def reject_listing(admin_id: int, listing_id: int) -> dict[str, Any]:
    user = get_user(admin_id)
    if not user or user["role"] != "admin":
        return {"ok": False, "error": "admin only"}
    with Session(engine) as session:
        listing = session.get(Listing, listing_id)
        if listing is None:
            return {"ok": False, "error": "listing not found"}
        if listing.status != "pending":
            return {"ok": False, "error": "listing is not pending"}
        listing.status = "rejected"
        session.add(listing)
        session.commit()
        session.refresh(listing)
        return {"ok": True, "listing": listing.model_dump()}
