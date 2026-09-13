from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, AlertSubscription, WatershedZone
from app.schemas import AlertOut, AlertSubscribeIn

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Alert).where(Alert.resolved.is_(False)).order_by(Alert.triggered_at.desc())
    ).all()
    out = []
    for alert in rows:
        zone = db.get(WatershedZone, alert.zone_id)
        out.append(
            AlertOut(
                id=alert.id,
                zone_id=alert.zone_id,
                alert_type=alert.alert_type,
                triggered_at=alert.triggered_at,
                resolved=alert.resolved,
                zone_name=zone.name if zone else None,
            )
        )
    return out


@router.post("/subscribe")
def subscribe(payload: AlertSubscribeIn, db: Session = Depends(get_db)):
    sub = AlertSubscription(email=payload.email, zone_id=payload.zone_id)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"id": sub.id, "email": sub.email, "zone_id": sub.zone_id}
