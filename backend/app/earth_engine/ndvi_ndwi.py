"""Sentinel-2 NDVI / NDWI pipeline for rural (Tana) and urban (Nairobi) AOIs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import ee

from app.earth_engine.auth import initialize_ee


@dataclass
class NdviNdwiResult:
    current: float
    year_ago: float
    dry_season: float  # NDWI in driest month proxy
    ndvi_mean: float
    ndwi_mean: float
    bare_soil_pct: float


def tana_basin_aoi() -> ee.FeatureCollection:
    return ee.FeatureCollection("WWF/HydroSHEDS/v1/Basins/hybas_7").filterBounds(
        ee.Geometry.Point([37.65, -0.35])
    )


def nairobi_aoi() -> ee.FeatureCollection:
    """Urban Data Source 1 — Nairobi county from FAO GAUL."""
    return ee.FeatureCollection("FAO/GAUL/2015/level2").filter(
        ee.Filter.eq("ADM2_NAME", "Nairobi")
    )


def _region_from_zone(geom) -> ee.Geometry:
    if hasattr(geom, "desc"):
        return geom
    if isinstance(geom, dict):
        return ee.Geometry(geom)
    # WKT / GeoAlchemy WKBElement handled by caller converting to GeoJSON
    return ee.Geometry(geom)


def _add_indices(img: ee.Image) -> ee.Image:
    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")
    # Simple bare-soil proxy: low NDVI + low NDWI
    bare = (
        ndvi.lt(0.2)
        .And(ndwi.lt(0.0))
        .rename("BARE")
    )
    return img.addBands([ndvi, ndwi, bare])


def _s2_collection(region: ee.Geometry, start: str, end: str) -> ee.ImageCollection:
    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(region)
        .filterDate(start, end)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(_add_indices)
    )


def _mean_band(collection: ee.ImageCollection, band: str, region: ee.Geometry) -> float:
    image = collection.select(band).median()
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=20,
        maxPixels=1e9,
        bestEffort=True,
    )
    value = stats.get(band).getInfo()
    return float(value) if value is not None else 0.0


def _bare_soil_pct(collection: ee.ImageCollection, region: ee.Geometry) -> float:
    bare = collection.select("BARE").median()
    stats = bare.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=20,
        maxPixels=1e9,
        bestEffort=True,
    )
    frac = stats.get("BARE").getInfo()
    return round(float(frac or 0.0) * 100, 2)


def pull_latest_ndvi_ndwi(geom, urban: bool = False) -> NdviNdwiResult:
    """
    Pull Sentinel-2 NDVI/NDWI for a zone geometry.
    Set urban=True to use Nairobi GAUL boundary as AOI filter context
    without altering the index math (Section 6.1).
    """
    initialize_ee()
    region = _region_from_zone(geom)
    if urban:
        # Clip analysis to urban boundary intersection when requested
        region = region.intersection(nairobi_aoi().geometry(), 1)

    now = datetime.now(timezone.utc)
    end = now.strftime("%Y-%m-%d")
    start_12 = now.replace(year=now.year - 1).strftime("%Y-%m-%d")
    # Year-ago window: ~30 days around same calendar day last year
    ya_end = start_12
    ya_start = now.replace(year=now.year - 1, day=max(1, now.day - 15)).strftime("%Y-%m-%d")
    # Dry-season proxy for Kenya highlands: Jan–Feb
    dry_start = f"{now.year}-01-01"
    dry_end = f"{now.year}-02-28"
    recent_start = now.replace(month=max(1, now.month - 1)).strftime("%Y-%m-%d")

    recent = _s2_collection(region, recent_start, end)
    year_ago = _s2_collection(region, ya_start, ya_end)
    dry = _s2_collection(region, dry_start, dry_end)
    full_year = _s2_collection(region, start_12, end)

    ndvi_current = _mean_band(recent, "NDVI", region)
    ndvi_year_ago = _mean_band(year_ago, "NDVI", region)
    ndwi_mean = _mean_band(full_year, "NDWI", region)
    ndwi_dry = _mean_band(dry, "NDWI", region)
    bare = _bare_soil_pct(full_year, region)

    return NdviNdwiResult(
        current=ndvi_current,
        year_ago=ndvi_year_ago,
        dry_season=ndwi_dry,
        ndvi_mean=ndvi_current,
        ndwi_mean=ndwi_mean,
        bare_soil_pct=bare,
    )


def get_chirps_anomaly(geom) -> float:
    """
    CHIRPS rainfall anomaly: % deviation of last 30 days vs 10-year mean
    for the same calendar window.
    """
    initialize_ee()
    region = _region_from_zone(geom)
    now = datetime.now(timezone.utc)
    end = ee.Date(now.strftime("%Y-%m-%d"))
    start = end.advance(-30, "day")

    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterBounds(region)

    recent = (
        chirps.filterDate(start, end)
        .sum()
        .reduceRegion(ee.Reducer.mean(), region, 5000, bestEffort=True)
        .get("precipitation")
    )

    # Build 10-year climatology for same DOY window
    years = ee.List.sequence(now.year - 10, now.year - 1)

    def yearly_sum(y):
        y = ee.Number(y)
        s = ee.Date.fromYMD(y, now.month, min(now.day, 28)).advance(-30, "day")
        e = ee.Date.fromYMD(y, now.month, min(now.day, 28))
        return (
            chirps.filterDate(s, e)
            .sum()
            .reduceRegion(ee.Reducer.mean(), region, 5000, bestEffort=True)
            .get("precipitation")
        )

    hist = ee.Array(years.map(yearly_sum))
    hist_mean = hist.reduce(ee.Reducer.mean(), [0]).get([0])

    recent_val = ee.Number(recent)
    mean_val = ee.Number(hist_mean)
    anomaly = recent_val.subtract(mean_val).divide(mean_val.max(1)).multiply(100)
    return float(anomaly.getInfo())
