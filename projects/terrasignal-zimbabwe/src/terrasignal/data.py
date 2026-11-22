"""Live-data access only. No synthetic observations are stored in this project."""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

import httpx

STAC_URL = "https://stac.dataspace.copernicus.eu/v1/search"
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv"


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
        raise ProviderUnavailable(f"Copernicus STAC request failed: {exc}") from exc

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


async def firms_country_fires(days: int = 2) -> dict[str, Any]:
    """Retrieve real VIIRS active-fire detections for Zimbabwe from NASA FIRMS."""
    map_key = os.getenv("NASA_FIRMS_MAP_KEY")
    if not map_key:
        raise ProviderUnavailable(
            "NASA FIRMS is not configured. Set NASA_FIRMS_MAP_KEY using a free key "
            "from https://firms.modaps.eosdis.nasa.gov/api/map_key/"
        )
    days = max(1, min(days, 10))
    url = f"{FIRMS_URL}/{map_key}/VIIRS_SNPP_NRT/ZWE/{days}"
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.get(url)
            response.raise_for_status()
            csv_text = response.text
    except httpx.HTTPError as exc:
        raise ProviderUnavailable(f"NASA FIRMS request failed: {exc}") from exc

    import csv
    import io

    rows = list(csv.DictReader(io.StringIO(csv_text)))
    return {
        "source": "NASA FIRMS",
        "product": "VIIRS_SNPP_NRT",
        "country": "ZWE",
        "days": days,
        "count": len(rows),
        "items": rows,
        "caveat": (
            "Satellite thermal anomalies are detections, not confirmed ground fires. "
            "Use confidence, acquisition time and field verification."
        ),
    }
