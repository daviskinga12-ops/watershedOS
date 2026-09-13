from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "watershed_zones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("zone_type", sa.Text(), nullable=False),
        sa.Column("geom", Geometry("POLYGON", srid=4326), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint("zone_type IN ('rural', 'urban')", name="ck_zone_type"),
    )

    op.create_table(
        "health_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("watershed_zones.id")),
        sa.Column("score_date", sa.Date(), nullable=False),
        sa.Column("ndvi_mean", sa.Numeric()),
        sa.Column("ndwi_mean", sa.Numeric()),
        sa.Column("bare_soil_pct", sa.Numeric()),
        sa.Column("rainfall_mm", sa.Numeric()),
        sa.Column("health_score", sa.Numeric()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "health_score IS NULL OR (health_score BETWEEN 0 AND 100)",
            name="ck_health_score_range",
        ),
    )

    op.create_table(
        "restoration_activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("watershed_zones.id")),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("activity_type", sa.Text(), nullable=False),
        sa.Column("area_hectares", sa.Numeric(), nullable=False),
        sa.Column("logged_by", sa.Text()),
        sa.Column("ndvi_improved", sa.Boolean()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.CheckConstraint(
            "activity_type IN ('planting', 'gabion', 'terrace')",
            name="ck_activity_type",
        ),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("watershed_zones.id")),
        sa.Column("alert_type", sa.Text(), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("resolved", sa.Boolean(), server_default=sa.text("false")),
    )

    op.create_table(
        "carbon_estimates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("watershed_zones.id")),
        sa.Column("activity_type", sa.Text(), nullable=False),
        sa.Column("verra_tco2e", sa.Numeric()),
        sa.Column("gold_standard_tco2e", sa.Numeric()),
        sa.Column("price_usd_per_tco2e", sa.Numeric()),
        sa.Column("estimated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "alert_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("watershed_zones.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_index("idx_health_scores_zone_date", "health_scores", ["zone_id", "score_date"])
    op.execute("CREATE INDEX idx_zones_geom ON watershed_zones USING GIST (geom)")


def downgrade() -> None:
    op.drop_index("idx_zones_geom", table_name="watershed_zones")
    op.drop_index("idx_health_scores_zone_date", table_name="health_scores")
    op.drop_table("alert_subscriptions")
    op.drop_table("carbon_estimates")
    op.drop_table("alerts")
    op.drop_table("restoration_activities")
    op.drop_table("health_scores")
    op.drop_table("watershed_zones")
