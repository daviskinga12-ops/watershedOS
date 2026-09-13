"""Landsat Band 10 thermal — urban heat island layer (Week 9)."""

from __future__ import annotations

import ee

from app.earth_engine.auth import initialize_ee
from app.earth_engine.ndvi_ndwi import nairobi_aoi


def landsat_thermal_celsius(
    start: str = "2024-01-01",
    end: str = "2024-12-31",
) -> ee.Image:
    """
    ST_B10 scaled Kelvin DN → Celsius:
    celsius = (ST_B10 * 0.00341802 + 149.0) - 273.15
    """
    initialize_ee()
    urban_boundary = nairobi_aoi()
    landsat = (
        ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
        .filterBounds(urban_boundary)
        .filterDate(start, end)
        .select("ST_B10")
        .median()
    )
    celsius = landsat.multiply(0.00341802).add(149.0).subtract(273.15).rename("temp_c")
    return celsius.clip(urban_boundary.geometry())


def mean_surface_temp_c(geom, start: str = "2024-01-01", end: str = "2024-12-31") -> float:
    initialize_ee()
    image = landsat_thermal_celsius(start, end)
    region = ee.Geometry(geom) if isinstance(geom, dict) else geom
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=30,
        maxPixels=1e9,
        bestEffort=True,
    )
    value = stats.get("temp_c").getInfo()
    return float(value) if value is not None else 0.0
