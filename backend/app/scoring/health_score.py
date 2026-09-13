"""
Watershed health scoring algorithm.

Weighting [SPEC GAP — AUTHORED]: 40% vegetation trend, 30% bare soil
exposure, 30% dry-season water presence. Rainfall anomaly is used to
DISCOUNT the vegetation-trend penalty when a drought (not human
degradation) explains the NDVI drop — per the Notion note to
"distinguish drought-driven vs. human-driven degradation."

Adjust these weights against ground-truth validation in Week 6
before treating scores as authoritative.
"""

# Adjustable constants — not fixed truth until Week 6 validation
VEG_TREND_WEIGHT = 0.40
BARE_SOIL_WEIGHT = 0.30
WATER_WEIGHT = 0.30


def compute_health_score(
    ndvi_current: float,
    ndvi_12mo_ago: float,
    bare_soil_pct: float,  # 0–100, from Sentinel-2 classification
    ndwi_dry_season: float,  # -1 to 1, measured in the driest month of the year
    rainfall_anomaly_pct: float,  # from CHIRPS, % deviation from 10-yr average
) -> float:
    """
    Returns a 0-100 watershed health score.
    """
    # 1. Vegetation trend component (0-1)
    ndvi_change = ndvi_current - ndvi_12mo_ago
    drought_discount = max(0.0, 1 - abs(rainfall_anomaly_pct) / 100)
    veg_trend_score = max(0.0, min(1.0, 0.5 + (ndvi_change * drought_discount) * 2.5))

    # 2. Bare soil exposure component (0-1) — lower bare soil = healthier
    bare_soil_score = max(0.0, min(1.0, 1 - (bare_soil_pct / 100)))

    # 3. Dry-season water presence component (0-1)
    water_score = max(0.0, min(1.0, (ndwi_dry_season + 1) / 2))

    weighted = (
        (VEG_TREND_WEIGHT * veg_trend_score)
        + (BARE_SOIL_WEIGHT * bare_soil_score)
        + (WATER_WEIGHT * water_score)
    )
    return round(weighted * 100, 1)
