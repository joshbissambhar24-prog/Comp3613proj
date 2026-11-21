"""Email campaign compose / send through shared Observer mechanism.
Kyle owns Sprint 2 task #14. Existing public service signatures are retained.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from sqlmodel import Session, select
from app.database import engine
from app.models.campaign import Campaign
from app.services import notifications
from app.services.board_auth import get_user
from app.services.recipient_policy import verified_alumni_ids


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_draft(admin_id: int, *, subject: str, body: str) -> dict[str, Any]:
    user = get_user(admin_id)
    if not user or user["role"] != "admin":
        return {"ok": False, "error": "admin only"}
    with Session(engine) as session:
        campaign = Campaign(admin_id=admin_id, subject=subject, body=body,
                            status="draft", created_at=_now(), sent_at=None)
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        return {"ok": True, "campaign": campaign.model_dump()}


def list_campaigns() -> list[dict[str, Any]]:
    with Session(engine) as session:
        return [row.model_dump() for row in session.exec(
            select(Campaign).order_by(Campaign.id.desc())
        ).all()]


def send_campaign(admin_id: int, campaign_id: int) -> dict[str, Any]:
    user = get_user(admin_id)
    if not user or user["role"] != "admin":
        return {"ok": False, "error": "admin only"}
    with Session(engine) as session:
        campaign = session.get(Campaign, campaign_id)
        if campaign is None:
            return {"ok": False, "error": "campaign not found"}
        if campaign.status != "draft":
            return {"ok": False, "error": "campaign already sent"}
        campaign.status = "sent"
        campaign.sent_at = _now()
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        row = campaign.model_dump()

    report = notifications.notify({
        "event_type": "campaign.sent",
        "source_key": f"campaign:{campaign_id}",
        "recipient_ids": verified_alumni_ids(),
        "message": f"Campaign: {row['subject']} - {row['body'][:120]}",
    })
    return {"ok": True, "campaign": row, "notification_failures": report.failed}
