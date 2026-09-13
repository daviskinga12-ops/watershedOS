"""5-day automated satellite pull + restoration NDVI follow-up."""

from __future__ import annotations

from datetime import date, timedelta

from geoalchemy2.shape import to_shape
from sqlalchemy import select

from app.database import SessionLocal
from app.earth_engine.ndvi_ndwi import get_chirps_anomaly, pull_latest_ndvi_ndwi
from app.models import Alert, HealthScore, RestorationActivity, WatershedZone
from app.scoring.health_score import compute_health_score
from app.tasks.celery_app import celery_app


def _zone_geojson(zone: WatershedZone) -> dict:
    shape = to_shape(zone.geom)
    return shape.__geo_interface__


def get_all_zones(db):
    return db.scalars(select(WatershedZone)).all()


def save_health_score(db, zone_id, ndvi, ndwi_mean, bare_soil, rainfall, score):
    row = HealthScore(
        zone_id=zone_id,
        score_date=date.today(),
        ndvi_mean=ndvi.ndvi_mean,
        ndwi_mean=ndwi_mean,
        bare_soil_pct=bare_soil,
        rainfall_mm=rainfall,
        health_score=score,
    )
    db.add(row)
    return row


def raise_alert(db, zone_id: int, alert_type: str):
    existing = db.scalars(
        select(Alert).where(
            Alert.zone_id == zone_id,
            Alert.alert_type == alert_type,
            Alert.resolved.is_(False),
        )
    ).first()
    if existing:
        return existing
    alert = Alert(zone_id=zone_id, alert_type=alert_type)
    db.add(alert)
    return alert


@celery_app.task(name="app.tasks.scheduled_pull.run_pipeline")
def run_pipeline():
    db = SessionLocal()
    try:
        for zone in get_all_zones(db):
            geom = _zone_geojson(zone)
            urban = zone.zone_type == "urban"
            ndvi = pull_latest_ndvi_ndwi(geom, urban=urban)
            rainfall = get_chirps_anomaly(geom)
            score = compute_health_score(
                ndvi.current,
                ndvi.year_ago,
                ndvi.bare_soil_pct,
                ndvi.dry_season,
                rainfall,
            )
            save_health_score(
                db,
                zone.id,
                ndvi,
                ndvi.ndwi_mean,
                ndvi.bare_soil_pct,
                rainfall,
                score,
            )
            if score < 40:
                raise_alert(db, zone.id, "health_score_low")
        db.commit()
        return {"status": "ok", "zones": len(get_all_zones(db))}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name="app.tasks.scheduled_pull.check_restoration_ndvi")
def check_restoration_ndvi():
    """Three months after activity_date, set ndvi_improved from Sentinel-2."""
    db = SessionLocal()
    try:
        cutoff = date.today() - timedelta(days=90)
        pending = db.scalars(
            select(RestorationActivity).where(
                RestorationActivity.ndvi_improved.is_(None),
                RestorationActivity.activity_date <= cutoff,
            )
        ).all()
        for activity in pending:
            zone = db.get(WatershedZone, activity.zone_id)
            if not zone:
                continue
            geom = _zone_geojson(zone)
            result = pull_latest_ndvi_ndwi(geom, urban=zone.zone_type == "urban")
            # Improved if current NDVI exceeds year-ago (post-restoration rebound)
            activity.ndvi_improved = result.current > result.year_ago
        db.commit()
        return {"checked": len(pending)}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
