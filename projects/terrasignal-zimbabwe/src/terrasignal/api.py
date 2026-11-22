"""FastAPI service for the TerraSignal Zimbabwe prototype."""

from fastapi import FastAPI

from terrasignal.data import ALERTS, REGIONS, summary_payload

app = FastAPI(
    title="TerraSignal Zimbabwe API",
    version="0.1.0",
    description="Environmental intelligence prototype. Bundled records are illustrative demo data.",
)

@app.get("/health", tags=["operations"])
def health() -> dict:
    return {"status": "ok", "service": "terrasignal-zimbabwe"}

@app.get("/api/v1/summary", tags=["dashboard"])
def get_summary() -> dict:
    return summary_payload()

@app.get("/api/v1/regions", tags=["geospatial"])
def get_regions() -> dict:
    return {"mode": "DEMO", "items": REGIONS}

@app.get("/api/v1/alerts", tags=["monitoring"])
def get_alerts() -> dict:
    return {"mode": "DEMO", "items": ALERTS}
