"""OpenLandMap soil organic carbon (Week 12 / carbon calculator support)."""

from __future__ import annotations

import ee

from app.earth_engine.auth import initialize_ee


def soil_organic_carbon_0_5cm() -> ee.Image:
    initialize_ee()
    return ee.Image("OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02").select("b0")


def mean_soil_carbon(geom) -> float:
    """Mean soil organic carbon (g/kg) at 0–5 cm for the given geometry."""
    initialize_ee()
    image = soil_organic_carbon_0_5cm()
    region = ee.Geometry(geom) if isinstance(geom, dict) else geom
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region,
        scale=250,
        maxPixels=1e9,
        bestEffort=True,
    )
    value = stats.get("b0").getInfo()
    return float(value) if value is not None else 0.0
