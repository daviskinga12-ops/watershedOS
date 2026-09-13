"""
Carbon credit calculator.

[SPEC GAP — AUTHORED / ACTION REQUIRED]: VM0047 above-ground-biomass formula
must be extracted from the Verra PDF. Until then, estimate_biomass() is a
clearly-labeled NDVI-to-biomass regression PROXY — not Verra-compliant.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CarbonEstimate, WatershedZone
from app.schemas import CarbonEstimateOut, CarbonEstimateRequest

router = APIRouter(prefix="/carbon", tags=["carbon"])

DISCLAIMER = (
    "estimate — pending VM0047 methodology. "
    "Placeholder NDVI→biomass proxy only; not a Verra-compliant estimate."
)

# Placeholder market price (USD / tCO2e) — refresh quarterly from carboncredits.com
DEFAULT_PRICE_USD_PER_TCO2E = 8.50

# Activity factors for placeholder (tCO2e / ha / yr) before NDVI scaling
ACTIVITY_BASE_TCO2E = {
    "planting": 4.0,
    "gabion": 0.5,
    "terrace": 1.2,
}


def estimate_biomass(ndvi_mean: float, area_hectares: float, activity_type: str) -> float:
    """
    PLACEHOLDER — simple NDVI-to-biomass regression proxy.
    Replace with VM0047 coefficients once extracted from Verra PDF.
    """
    base = ACTIVITY_BASE_TCO2E.get(activity_type, 1.0)
    # Scale by NDVI (0–1-ish): healthier vegetation → more AGB proxy
    ndvi_factor = max(0.1, min(1.5, (ndvi_mean + 0.2) * 1.2))
    return round(base * ndvi_factor * area_hectares, 3)


@router.post("/estimate", response_model=CarbonEstimateOut)
def estimate_carbon(payload: CarbonEstimateRequest, db: Session = Depends(get_db)):
    zone = db.get(WatershedZone, payload.zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    tco2e = estimate_biomass(payload.ndvi_mean or 0.4, payload.area_hectares, payload.activity_type)
    # Gold Standard placeholder: slight discount vs Verra proxy pathway
    verra = tco2e
    gold = round(tco2e * 0.92, 3)
    price = DEFAULT_PRICE_USD_PER_TCO2E

    row = CarbonEstimate(
        zone_id=payload.zone_id,
        activity_type=payload.activity_type,
        verra_tco2e=verra,
        gold_standard_tco2e=gold,
        price_usd_per_tco2e=price,
    )
    db.add(row)
    db.commit()

    return CarbonEstimateOut(
        zone_id=payload.zone_id,
        activity_type=payload.activity_type,
        verra_tco2e=verra,
        gold_standard_tco2e=gold,
        price_usd_per_tco2e=price,
        estimated_value_usd=round(verra * price, 2),
        disclaimer=DISCLAIMER,
        methodology="placeholder_ndvi_biomass_proxy",
    )
