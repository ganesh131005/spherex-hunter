"""
🚀 SPHEREx Hunter - Real-Time FastAPI Astronomical Backend
NASA Space Apps 2026 - Team RIP

Provides REST API endpoints for:
- Multi-epoch astronomical cutouts (Epoch 1, Epoch 2, Difference Map)
- 102-band near-infrared Spectral Energy Distribution (SED)
- Benchmark target metadata (WISE 0855, Barnard's Star, Epsilon Indi B, RW Aurigae, R Draconis)
- Citizen science candidate logging
"""

import os
import json
from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.services.cutout_engine import (
    fetch_real_cutout,
    get_102_band_spectrum,
    BENCHMARKS
)

app = FastAPI(
    title="SPHEREx Hunter Astronomical API",
    description="NASA Space Apps 2026 - Team RIP (Planet X & SPHEREx)",
    version="1.0.0"
)

# Enable CORS for all origins (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend directory for same-origin browsing
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# In-memory discovery ledger (persisted to JSON)
DISCOVERIES_FILE = os.path.join(os.path.dirname(__file__), "..", "07 - Team Memory & Sync", "candidate_discoveries.json")

class DiscoveryCandidate(BaseModel):
    ra: float
    dec: float
    object_type: str
    user_handle: str = "@citizen_scientist"
    notes: Optional[str] = ""
    target_name: Optional[str] = "Unknown"

@app.get("/")
def root():
    return {
        "service": "SPHEREx Hunter Astronomy Backend",
        "team": "RIP (Coimbatore, India)",
        "challenge": "Planet X and SPHEREx",
        "docs_url": "/docs",
        "endpoints": [
            "/api/health",
            "/api/targets",
            "/api/cutout?ra=133.79513&dec=-7.24515&target=wise0855",
            "/api/spectrum?ra=133.79513&dec=-7.24515&target=wise0855",
            "/api/discoveries"
        ]
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "engine": "Astropy + Astroquery + FastAPI",
        "archive": "NASA IRSA / SkyView Connected",
        "active_epochs": 2
    }

@app.get("/api/targets")
def get_benchmark_targets():
    """Returns the 5 NASA benchmark target specifications."""
    return [
        {
            "id": k,
            "name": v["name"],
            "ra": v["ra"],
            "dec": v["dec"],
            "type": v["type"],
            "temp_k": v["temp_k"],
            "variability": v.get("variability", 1.0)
        }
        for k, v in BENCHMARKS.items()
    ]

@app.get("/api/cutout")
def get_cutout(
    ra: float = Query(..., description="Right Ascension in decimal degrees"),
    dec: float = Query(..., description="Declination in decimal degrees"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key (wise0855, barnard, etc.)")
):
    """
    Fetches real astronomical data for the given coordinates, generates Epoch 1 & Epoch 2
    with true proper motion or variable star flares, and returns the difference map.
    """
    try:
        data = fetch_real_cutout(ra=ra, dec=dec, fov_arcmin=fov, target_key=target)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/spectrum")
def get_spectrum(
    ra: float = Query(..., description="Right Ascension in decimal degrees"),
    dec: float = Query(..., description="Declination in decimal degrees"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Returns the 102 near-infrared spectral bands (0.75 - 5.0 μm) with molecular detections."""
    try:
        spectrum = get_102_band_spectrum(ra=ra, dec=dec, target_key=target)
        return spectrum
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/discoveries")
def get_discoveries():
    """Returns community discoveries logged by users."""
    if os.path.exists(DISCOVERIES_FILE):
        try:
            with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

@app.post("/api/flag")
def flag_candidate(candidate: DiscoveryCandidate):
    """Logs a new candidate into the community discovery list."""
    discoveries = []
    if os.path.exists(DISCOVERIES_FILE):
        try:
            with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
                discoveries = json.load(f)
        except Exception:
            discoveries = []
            
    entry = candidate.model_dump()
    entry["timestamp"] = "2026-11-12T20:50:00Z"
    discoveries.insert(0, entry)
    
    with open(DISCOVERIES_FILE, "w", encoding="utf-8") as f:
        json.dump(discoveries[:50], f, indent=2)
        
    return {"status": "recorded", "entry": entry}

if __name__ == "__main__":
    import uvicorn
    print("Starting SPHEREx Hunter Astronomical Backend on http://localhost:8000...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
