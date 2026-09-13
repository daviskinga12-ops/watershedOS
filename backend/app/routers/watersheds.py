from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HealthScore, WatershedZone
from app.schemas import HealthScoreOut, WatershedZoneOut

router = APIRouter(prefix="/watersheds", tags=["watersheds"])


def _zone_to_out(zone: WatershedZone, latest_score: Optional[float] = None) -> WatershedZoneOut:
    shape = to_shape(zone.geom)
    return WatershedZoneOut(
        id=zone.id,
        name=zone.name,
        zone_type=zone.zone_type,
        geojson=shape.__geo_interface__,
        latest_health_score=latest_score,
    )


@router.get("", response_model=list[WatershedZoneOut])
def list_watersheds(db: Session = Depends(get_db)):
    """
    Zone-level polygons only — never parcel-level landowner data (Section 7).
    """
    zones = db.scalars(select(WatershedZone)).all()
    results = []
    for zone in zones:
        latest = db.scalars(
            select(HealthScore)
            .where(HealthScore.zone_id == zone.id)
            .order_by(HealthScore.score_date.desc())
            .limit(1)
        ).first()
        score = float(latest.health_score) if latest and latest.health_score is not None else None
        results.append(_zone_to_out(zone, score))
    return results


@router.get("/{zone_id}/scores", response_model=list[HealthScoreOut])
def zone_scores(zone_id: int, db: Session = Depends(get_db)):
    zone = db.get(WatershedZone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    rows = db.scalars(
        select(HealthScore)
        .where(HealthScore.zone_id == zone_id)
        .order_by(HealthScore.score_date.asc())
    ).all()
    return rows


@router.get("/{zone_id}/health-score", response_model=HealthScoreOut)
def latest_health_score(zone_id: int, db: Session = Depends(get_db)):
    zone = db.get(WatershedZone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    row = db.scalars(
        select(HealthScore)
        .where(HealthScore.zone_id == zone_id)
        .order_by(HealthScore.score_date.desc())
        .limit(1)
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="No health score yet")
    return row
