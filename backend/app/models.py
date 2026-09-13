from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    func,
)
from geoalchemy2 import Geometry

from app.database import Base


class WatershedZone(Base):
    __tablename__ = "watershed_zones"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    zone_type = Column(Text, nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("zone_type IN ('rural', 'urban')", name="ck_zone_type"),
    )


class HealthScore(Base):
    __tablename__ = "health_scores"

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("watershed_zones.id"))
    score_date = Column(Date, nullable=False)
    ndvi_mean = Column(Numeric)
    ndwi_mean = Column(Numeric)
    bare_soil_pct = Column(Numeric)
    rainfall_mm = Column(Numeric)
    health_score = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "health_score IS NULL OR (health_score BETWEEN 0 AND 100)",
            name="ck_health_score_range",
        ),
    )


class RestorationActivity(Base):
    __tablename__ = "restoration_activities"

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("watershed_zones.id"))
    activity_date = Column(Date, nullable=False)
    activity_type = Column(Text, nullable=False)
    area_hectares = Column(Numeric, nullable=False)
    logged_by = Column(Text)
    ndvi_improved = Column(Boolean)  # filled 3 months later by scheduled check
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "activity_type IN ('planting', 'gabion', 'terrace')",
            name="ck_activity_type",
        ),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("watershed_zones.id"))
    alert_type = Column(Text, nullable=False)
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Boolean, default=False)


class CarbonEstimate(Base):
    __tablename__ = "carbon_estimates"

    id = Column(Integer, primary_key=True)
    zone_id = Column(Integer, ForeignKey("watershed_zones.id"))
    activity_type = Column(Text, nullable=False)
    verra_tco2e = Column(Numeric)
    gold_standard_tco2e = Column(Numeric)
    price_usd_per_tco2e = Column(Numeric)
    estimated_at = Column(DateTime(timezone=True), server_default=func.now())


class AlertSubscription(Base):
    """Email/webhook subscriptions for alert notifications (POST /alerts/subscribe)."""

    __tablename__ = "alert_subscriptions"

    id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=False)
    zone_id = Column(Integer, ForeignKey("watershed_zones.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
