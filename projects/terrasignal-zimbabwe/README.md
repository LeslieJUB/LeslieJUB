# TerraSignal Zimbabwe
**Earth-observation intelligence for Zimbabwe.**

TerraSignal is a geospatial monitoring platform that discovers and analyses satellite observations to support forestry, conservation, agriculture and environmental-risk teams.

## Live integrations in this release
- **Copernicus Data Space Ecosystem STAC API:** live discovery of Sentinel-2 L2A catalogue items intersecting Zimbabwe, with acquisition timestamps, cloud-cover metadata, platform, collection and asset references.
- **NASA FIRMS:** live country-level VIIRS SNPP near-real-time thermal-anomaly records for Zimbabwe. Requires a free NASA FIRMS map key.

These are genuine upstream records. Sentinel scene discovery is catalogue metadata only; it does **not** yet calculate NDVI or establish vegetation loss. FIRMS thermal anomalies are not confirmed ground fires.

## Run locally
Python 3.12+ recommended.
```bash
cd projects/terrasignal-zimbabwe
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```
Get a free NASA FIRMS API key: https://firms.modaps.eosdis.nasa.gov/api/map_key/
```bash
export NASA_FIRMS_MAP_KEY="YOUR_KEY"
uvicorn terrasignal.api:app --app-dir src --reload
```
In a second terminal:
```bash
python -m http.server 8080 --directory web
```
Open http://127.0.0.1:8080. API docs: http://127.0.0.1:8000/docs.

The dashboard attempts both live providers independently. If a provider is unavailable or the FIRMS key is missing, it displays the error instead of filling the screen with synthetic records.

## API
- GET `/health`
- GET `/api/v1/sentinel/scenes?start=YYYY-MM-DD&end=YYYY-MM-DD&max_cloud=30`
- GET `/api/v1/fires?days=2` (1–10 days)

## Data integrity
1. Preserve provider, product, acquisition time and query parameters with each observation.
2. Distinguish catalogue availability from analysis outputs.
3. Treat thermal anomalies as detections, not verified fires.
4. Never generate synthetic observations or silently substitute demo values.
5. Show missing credentials, provider errors and empty results explicitly.
6. Add quality checks, uncertainty and field validation before operational alerts.

## Engineering roadmap
1. Live Sentinel-2 scene discovery and NASA FIRMS ingestion (current).
2. Cloud/shadow masking and Sentinel-2 surface-reflectance processing.
3. NDVI/EVI time series with seasonal baselines and change statistics.
4. CHIRPS rainfall time series and anomaly analysis.
5. Zimbabwe administrative boundaries and user-defined monitoring areas.
6. PostGIS storage, reproducible processing jobs, alert audit trail and exports.
7. Backtested predictive models with calibrated uncertainty and monitoring.

## Technology
FastAPI, Python, httpx, Leaflet, Copernicus STAC, NASA FIRMS. Planned: STAC asset processing, Rasterio, GeoPandas, Xarray, PostGIS and CHIRPS.
