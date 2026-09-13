from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class WatershedZoneOut(BaseModel):
    id: int
    name: str
    zone_type: Literal["rural", "urban"]
    geojson: dict
    latest_health_score: Optional[float] = None

    model_config = {"from_attributes": True}


class HealthScoreOut(BaseModel):
    id: int
    zone_id: int
    score_date: date
    ndvi_mean: Optional[float] = None
    ndwi_mean: Optional[float] = None
    bare_soil_pct: Optional[float] = None
    rainfall_mm: Optional[float] = None
    health_score: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    zone_id: int
    alert_type: str
    triggered_at: Optional[datetime] = None
    resolved: bool = False
    zone_name: Optional[str] = None

    model_config = {"from_attributes": True}


class AlertSubscribeIn(BaseModel):
    email: EmailStr
    zone_id: Optional[int] = None


class RestorationCreate(BaseModel):
    zone_id: int
    activity_date: date
    activity_type: Literal["planting", "gabion", "terrace"]
    area_hectares: float = Field(gt=0)
    logged_by: Optional[str] = None


class RestorationOut(BaseModel):
    id: int
    zone_id: int
    activity_date: date
    activity_type: str
    area_hectares: float
    logged_by: Optional[str] = None
    ndvi_improved: Optional[bool] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CarbonEstimateRequest(BaseModel):
    zone_id: int
    activity_type: Literal["planting", "gabion", "terrace"]
    area_hectares: float = Field(gt=0)
    ndvi_mean: Optional[float] = Field(default=0.4, ge=-1, le=1)


class CarbonEstimateOut(BaseModel):
    zone_id: int
    activity_type: str
    verra_tco2e: float
    gold_standard_tco2e: float
    price_usd_per_tco2e: float
    estimated_value_usd: float
    disclaimer: str
    methodology: str
