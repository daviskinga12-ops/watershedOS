"""Seed the Tana River upper basin as a rural watershed_zones row."""

from __future__ import annotations

from geoalchemy2.shape import from_shape
from shapely.geometry import box
from sqlalchemy import select

from app.database import SessionLocal
from app.models import WatershedZone

# Approximate bounding box around HydroSHEDS point [37.65, -0.35]
# Replace with actual basin polygon when EE export is available.
TANA_BBOX = box(36.8, -1.2, 38.5, 0.5)


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.scalars(
            select(WatershedZone).where(WatershedZone.name == "Tana River upper basin")
        ).first()
        if existing:
            print(f"Already seeded: id={existing.id}")
            return
        zone = WatershedZone(
            name="Tana River upper basin",
            zone_type="rural",
            geom=from_shape(TANA_BBOX, srid=4326),
        )
        db.add(zone)
        db.commit()
        db.refresh(zone)
        print(f"Seeded Tana basin zone id={zone.id}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
