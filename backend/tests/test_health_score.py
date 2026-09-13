"""Unit tests for health scoring — no DB or Earth Engine required."""

from app.scoring.health_score import compute_health_score


def test_healthy_watershed_scores_high():
    score = compute_health_score(
        ndvi_current=0.65,
        ndvi_12mo_ago=0.55,
        bare_soil_pct=10,
        ndwi_dry_season=0.2,
        rainfall_anomaly_pct=0,
    )
    assert score >= 70


def test_degraded_watershed_scores_low():
    score = compute_health_score(
        ndvi_current=0.15,
        ndvi_12mo_ago=0.45,
        bare_soil_pct=70,
        ndwi_dry_season=-0.5,
        rainfall_anomaly_pct=0,
    )
    assert score < 40


def test_drought_discounts_vegetation_penalty():
    without_drought = compute_health_score(0.2, 0.5, 30, 0.0, 0)
    with_drought = compute_health_score(0.2, 0.5, 30, 0.0, -40)
    assert with_drought >= without_drought


def test_score_clamped_0_100():
    score = compute_health_score(1.0, -1.0, 0, 1.0, 0)
    assert 0 <= score <= 100
