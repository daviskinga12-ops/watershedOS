"""Sentinel-1 SAR — flood risk / impervious surface (Week 11).

High VV backscatter = impervious surface (roads, buildings).
Very low VV during rainfall = flood water.
SAR works through cloud cover — important for Nairobi.
"""

from __future__ import annotations

import ee

from app.earth_engine.auth import initialize_ee
from app.earth_engine.ndvi_ndwi import nairobi_aoi


def sentinel1_vv_vh(
    start: str | None = None,
    end: str | None = None,
) -> ee.Image:
    initialize_ee()
    urban_boundary = nairobi_aoi()
    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filterBounds(urban_boundary)
        .select(["VV", "VH"])
    )
    if start and end:
        collection = collection.filterDate(start, end)
    return collection.median().clip(urban_boundary.geometry())


def impervious_and_flood_stats(geom) -> dict:
    """Return mean VV/VH and simple flood/impervious proxies for a zone."""
    initialize_ee()
    image = sentinel1_vv_vh()
    region = ee.Geometry(geom) if isinstance(geom, dict) else geom
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=10,
        maxPixels=1e9,
        bestEffort=True,
    ).getInfo()
    vv = float(stats.get("VV") or 0.0)
    vh = float(stats.get("VH") or 0.0)
    # Heuristic thresholds (adjust with ground truth)
    impervious_likely = vv > -8.0
    flood_likely = vv < -18.0
    return {
        "vv_db": vv,
        "vh_db": vh,
        "impervious_likely": impervious_likely,
        "flood_likely": flood_likely,
    }
