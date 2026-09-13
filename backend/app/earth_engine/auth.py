"""Earth Engine auth helper — uses GEE_SERVICE_ACCOUNT_JSON path or inline JSON."""

from __future__ import annotations

import json
import os
from functools import lru_cache

import ee


@lru_cache(maxsize=1)
def initialize_ee() -> None:
    creds_raw = os.getenv("GEE_SERVICE_ACCOUNT_JSON", "").strip()
    if not creds_raw:
        # Fall back to default application credentials / ee.Authenticate() locally
        ee.Initialize()
        return

    if os.path.isfile(creds_raw):
        key_path = creds_raw
        with open(creds_raw, encoding="utf-8") as f:
            info = json.load(f)
        credentials = ee.ServiceAccountCredentials(info["client_email"], key_path)
    else:
        import tempfile

        info = json.loads(creds_raw)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(info, tmp)
            key_path = tmp.name
        credentials = ee.ServiceAccountCredentials(info["client_email"], key_path)

    ee.Initialize(credentials)


def geom_from_wkt_or_geojson(geom) -> ee.Geometry:
    """Accept WKT string, GeoJSON dict, or ee.Geometry."""
    if isinstance(geom, ee.Geometry):
        return geom
    if isinstance(geom, dict):
        return ee.Geometry(geom)
    return ee.Geometry(geom)
