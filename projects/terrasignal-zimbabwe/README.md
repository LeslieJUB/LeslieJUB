# TerraSignal Zimbabwe
**Satellite intelligence & predictive monitoring for Zimbabwe.**

TerraSignal is an Earth-observation monitoring platform concept for forestry agencies, conservation organisations, agricultural operators, insurers and environmental programmes. It turns satellite-derived indicators and geospatial context into traceable signals that help teams prioritise field investigation.

> **Prototype disclosure:** This first release contains illustrative demonstration data. It is not a live satellite service, verified forest inventory, official risk assessment or operational forecast. Sentinel and NASA FIRMS integrations are planned, not yet connected.

## MVP
- Zimbabwe-focused monitoring dashboard and interactive map.
- Regional watchlist with transparent illustrative risk indices.
- Analyst alert workflow with confidence and review status.
- FastAPI endpoints for summary, regions, alerts and health.
- Clear provenance and data-integrity rules.

## Stack
Python 3.12+, FastAPI, Pydantic, Leaflet, PostgreSQL/PostGIS (planned), STAC, Sentinel-1/2 (planned), Rasterio, GeoPandas, Xarray, Docker and Terraform.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn terrasignal.api:app --reload
```
API docs: http://127.0.0.1:8000/docs

In a second terminal:
```bash
python -m http.server 8080 --directory web
```
Dashboard: http://127.0.0.1:8080

## Data integrity
1. Never label sample data as satellite observations.
2. Record source, acquisition time, processing version, spatial resolution and QA status for real observations.
3. Separate detected change from confirmed change; field validation is a separate state.
4. Display uncertainty and freshness alongside every operational risk signal.
5. Do not infer cause, tenure or legal status from imagery alone.

## Roadmap
1. Product foundation and API.
2. STAC discovery and Sentinel-2 vegetation indices for a pilot area.
3. Cloud-masked time-series baselines and change detection.
4. NASA FIRMS fire ingestion with source metadata and confidence.
5. PostGIS spatial zones, aggregation and analyst workflow.
6. Predictive models with backtesting, calibration and uncertainty.
7. Authentication, audit logs, alert subscriptions, observability and deployment.

## Commercial positioning
TerraSignal is a decision-support and prioritisation tool, not a substitute for field inspection or official environmental records. Potential users include forestry and conservation organisations, public agencies, agricultural estates, development programmes and environmental risk teams.
