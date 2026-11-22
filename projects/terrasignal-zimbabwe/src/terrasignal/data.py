"""Live-data access only. No synthetic observations are stored in this project."""

from __future__ import annotations

import csv
import io
import os
from datetime import date, timedelta
from typing import Any

import httpx

STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"
FIRMS_AREA_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
# Approximate Zimbabwe national bounding box, ordered west,south,east,north.
ZIMBABWE_BBOX = "25.219,-22.398,33.043,-15.609"


class ProviderUnavailable(RuntimeError):
    """Raised when an upstream Earth-observation provider cannot be reached."""


async def sentinel2_catalogue(
    start: date | None = None,
    end: date | None = None,
    max_cloud: int = 30,
) -> dict[str, Any]:
    """Discover actual Sentinel-2 L2A scenes intersecting Zimbabwe.

    This returns catalogue metadata, not processed vegetation measurements.
    """
    end = end or date.today()
    start = start or end - timedelta(days=30)
    payload = {
        "collections": ["sentinel-2-l2a"],
        "datetime": f"{start.isoformat()}T00:00:00Z/{end.isoformat()}T23:59:59Z",
        "intersects": {
            "type": "Polygon",
            "coordinates": [[
                [25.237, -22.417], [33.068, -22.417],
                [33.068, -15.609], [25.237, -15.609],
                [25.237, -22.417],
            ]],
        },
        "query": {"eo:cloud_cover": {"lte": max_cloud}},
        "limit": 100,
    }
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(STAC_URL, json=payload)
            response.raise_for_status()
            result = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ProviderUnavailable("Copernicus STAC request failed; check provider status and logs.") from exc

    features = result.get("features", [])
    items = []
    for feature in features:
        props = feature.get("properties", {})
        items.append({
            "id": feature.get("id"),
            "datetime": props.get("datetime"),
            "cloud_cover_percent": props.get("eo:cloud_cover"),
            "platform": props.get("platform"),
            "instruments": props.get("instruments"),
            "collection": feature.get("collection"),
            "bbox": feature.get("bbox"),
            "assets": {
                key: {"href": value.get("href"), "type": value.get("type")}
                for key, value in feature.get("assets", {}).items()
                if value.get("href")
            },
            "source": "Copernicus Data Space Ecosystem STAC",
        })
    return {
        "source": "Copernicus Data Space Ecosystem",
        "collection": "sentinel-2-l2a",
        "query_period": {"start": start.isoformat(), "end": end.isoformat()},
        "max_cloud_cover_percent": max_cloud,
        "count": len(items),
        "items": items,
        "interpretation": "Catalogue scenes only; no spectral indices have been computed.",
    }


async def firms_area_fires(days: int = 2) -> dict[str, Any]:
    """Retrieve real VIIRS thermal-anomaly detections intersecting Zimbabwe.

    Uses the FIRMS Area API. The legacy Country API currently returns HTTP 400.
    NOAA-21 is selected because Suomi-NPP/VIIRS observations ended in November 2026.
    """
    map_key = os.getenv("NASA_FIRMS_MAP_KEY")
    if not map_key:
        raise ProviderUnavailable(
            "NASA FIRMS is not configured. Set NASA_FIRMS_MAP_KEY using a free key "
            "from https://firms.modaps.eosdis.nasa.gov/api/map_key/"
        )
    days = max(1, min(days, 5))
    product = "VIIRS_NOAA21_NRT"
    url = f"{FIRMS_AREA_URL}/{map_key}/{product}/{ZIMBABWE_BBOX}/{days}"
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.get(url)
            if response.status_code >= 400:
                # Do not include the request URL: it contains the secret map key.
                detail = response.text[:300].strip()
                raise ProviderUnavailable(
                    f"NASA FIRMS returned HTTP {response.status_code}: {detail or 'No error detail'}"
                )
            csv_text = response.text
    except httpx.HTTPError as exc:
        # Avoid str(exc), which can include the full URL and expose the map key.
        raise ProviderUnavailable(f"NASA FIRMS network request failed ({type(exc).__name__}).") from exc

    rows = list(csv.DictReader(io.StringIO(csv_text)))
    return {
        "source": "NASA FIRMS",
        "product": product,
        "area": "Zimbabwe bounding box",
        "bbox_wsen": ZIMBABWE_BBOX,
        "days": days,
        "count": len(rows),
        "items": rows,
        "caveat": (
            "VIIRS thermal anomalies are satellite detections, not confirmed ground fires. "
            "The bounding box may include a small number of observations outside the national border; "
            "use confidence, acquisition time and boundary clipping before field decisions."
        ),
    }
