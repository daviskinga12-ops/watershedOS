from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RestorationActivity, WatershedZone
from app.schemas import RestorationCreate, RestorationOut

router = APIRouter(prefix="/restoration", tags=["restoration"])


@router.post("", response_model=RestorationOut)
def create_restoration(payload: RestorationCreate, db: Session = Depends(get_db)):
    zone = db.get(WatershedZone, payload.zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    row = RestorationActivity(
        zone_id=payload.zone_id,
        activity_date=payload.activity_date,
        activity_type=payload.activity_type,
        area_hectares=payload.area_hectares,
        logged_by=payload.logged_by,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("", response_model=list[RestorationOut])
def list_restoration(db: Session = Depends(get_db)):
    from sqlalchemy import select

    return db.scalars(select(RestorationActivity).order_by(RestorationActivity.activity_date.desc())).all()
