"""
Data retention / deletion policy (Section 7).

Policy (founder-adjustable defaults):
- alert_subscriptions (PII email): purge after 365 days unless renewed
- restoration_activities.logged_by (optional personal name): null after 730 days
- Raw personal field data must never be stored indefinitely by default

Satellite / zone / health_score aggregates are retained (non-personal, zone-level).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, update

from app.database import SessionLocal
from app.models import AlertSubscription, RestorationActivity
from app.tasks.celery_app import celery_app

SUBSCRIPTION_RETENTION_DAYS = 365
LOGGED_BY_RETENTION_DAYS = 730


@celery_app.task(name="app.tasks.retention.purge_expired_personal_data")
def purge_expired_personal_data():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        sub_cutoff = now - timedelta(days=SUBSCRIPTION_RETENTION_DAYS)
        name_cutoff = now - timedelta(days=LOGGED_BY_RETENTION_DAYS)

        deleted_subs = db.execute(
            delete(AlertSubscription).where(AlertSubscription.created_at < sub_cutoff)
        ).rowcount

        cleared_names = db.execute(
            update(RestorationActivity)
            .where(
                RestorationActivity.created_at < name_cutoff,
                RestorationActivity.logged_by.isnot(None),
            )
            .values(logged_by=None)
        ).rowcount

        db.commit()
        return {
            "subscriptions_deleted": deleted_subs or 0,
            "logged_by_cleared": cleared_names or 0,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
