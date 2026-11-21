"""Stephen: verified-only audience policy (Sprint 2 task #15)."""
from __future__ import annotations
from sqlmodel import Session, select
from app.database import engine
from app.models.user import User


def verified_alumni_ids() -> tuple[int, ...]:
    """Return verified alumni; never include admins or unverified accounts."""
    with Session(engine) as session:
        rows = session.exec(select(User).where(
            User.role == "alumni", User.email_verified == 1
        )).all()
        return tuple(row.id for row in rows if row.id is not None)
