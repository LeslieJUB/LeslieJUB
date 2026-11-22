"""TerraSignal API backed by live public Earth-observation catalogues."""

from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from terrasignal.data import (
    ProviderUnavailable,
    firms_area_fires,
    sentinel2_catalogue,
)

app = FastAPI(
    title="TerraSignal Zimbabwe",
    version="0.2.1",
    description=(
        "Live Earth-observation data discovery for Zimbabwe. "
        "Catalogue records and satellite detections retain source provenance."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", tags=["operations"])
def health() -> dict:
    return {"status": "ok", "service": "terrasignal-zimbabwe", "data_mode": "live-upstream"}


@app.get("/api/v1/sentinel/scenes", tags=["satellite"])
async def get_sentinel_scenes(
    start: date | None = None,
    end: date | None = None,
    max_cloud: int = Query(default=30, ge=0, le=100),
) -> dict:
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start must be on or before end")
    try:
        return await sentinel2_catalogue(start, end, max_cloud)
    except ProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/v1/fires", tags=["fire"])
async def get_fires(days: int = Query(default=2, ge=1, le=5)) -> dict:
    try:
        return await firms_area_fires(days)
    except ProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
