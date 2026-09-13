"""
Load Nairobi ward polygons from GeoJSON into watershed_zones (zone_type='urban').

Download Kenya ward-level boundaries from opendata.go.ke as GeoJSON, save as
nairobi_wards.geojson in the repo root or pass --path.

Usage:
  cd backend
  python -m scripts.load_nairobi_wards --path ../nairobi_wards.geojson
"""

from __future__ import annotations

import argparse

import geopandas as gpd
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import select

from app.database import SessionLocal
from app.models import WatershedZone


def _as_polygon(geom):
    if isinstance(geom, Polygon):
        return geom
    if isinstance(geom, MultiPolygon):
        # Store largest part as POLYGON (schema is POLYGON); split later if needed
        return max(geom.geoms, key=lambda g: g.area)
    raise ValueError(f"Unsupported geometry type: {type(geom)}")


def load_wards(path: str) -> int:
    gdf = gpd.read_file(path)
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(4326)

    name_col = next(
        (c for c in ("name", "NAME", "ward", "WARD", "Ward", "ADM2_NAME") if c in gdf.columns),
        None,
    )

    db = SessionLocal()
    inserted = 0
    try:
        for idx, row in gdf.iterrows():
            name = str(row[name_col]) if name_col else f"Nairobi ward {idx}"
            existing = db.scalars(
                select(WatershedZone).where(
                    WatershedZone.name == name,
                    WatershedZone.zone_type == "urban",
                )
            ).first()
            if existing:
                continue
            poly = _as_polygon(row.geometry)
            zone = WatershedZone(
                name=name,
                zone_type="urban",
                geom=from_shape(poly, srid=4326),
            )
            db.add(zone)
            inserted += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    return inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="nairobi_wards.geojson")
    args = parser.parse_args()
    n = load_wards(args.path)
    print(f"Inserted {n} urban watershed_zones rows")


if __name__ == "__main__":
    main()
