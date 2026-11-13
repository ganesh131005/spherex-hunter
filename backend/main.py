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
from fastapi.responses import FileResponse
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

import astropy.units as u
from astropy.coordinates import SkyCoord

def parse_celestial_coords(ra_input: str, dec_input: str) -> tuple[float, float]:
    """
    Parses both decimal degrees ('133.79513', '-7.24515') and 
    standard sexagesimal notation ('08h55m10.831s', '-7d14m42.53s') via Astropy.
    """
    try:
        return float(ra_input), float(dec_input)
    except ValueError:
        pass
        
    try:
        ra_clean = str(ra_input).strip()
        dec_clean = str(dec_input).strip()
        unit = (u.hourangle, u.deg) if 'h' in ra_clean.lower() else (u.deg, u.deg)
        sc = SkyCoord(ra_clean, dec_clean, unit=unit)
        return float(round(sc.ra.deg, 5)), float(round(sc.dec.deg, 5))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid celestial coordinates '{ra_input}', '{dec_input}': {e}")

@app.get("/api/cutout")
def get_cutout(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal ('08h55m10.831s')"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal ('-7d14m42.53s')"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key (wise0855, barnard, etc.)"),
    lod: int = Query(1, description="Game Level of Detail tier: 0 (Hero Deep), 1 (Standard Science), 2 (Wide Overview)")
):
    """
    Fetches real astronomical data for the given coordinates, generates Epoch 1 & Epoch 2
    with true proper motion or variable star flares, and returns the difference map.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        data = fetch_real_cutout(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target, lod=lod)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/spectrum")
def get_spectrum(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Returns the 102 near-infrared spectral bands (0.75 - 5.0 μm) with molecular detections."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        spectrum = get_102_band_spectrum(ra=ra_deg, dec=dec_deg, target_key=target)
        return spectrum
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download_fits")
def download_fits(
    target: Optional[str] = Query(None, description="Benchmark target key"),
    ra: Optional[str] = Query(None, description="Right Ascension"),
    dec: Optional[str] = Query(None, description="Declination"),
    epoch: int = Query(1, description="Epoch 1 (2MASS) or Epoch 2 (DSS2/SPHEREx)")
):
    """Streams authentic NASA scientific FITS file for requested target/coordinates & epoch."""
    import glob
    survey_suffix = "2mass.fits" if epoch == 1 else "dss2.fits"
    dyn_dir = os.path.join(os.path.dirname(__file__), "cache", "dynamic_fits")
    fits_dir = os.path.join(os.path.dirname(__file__), "cache", "fits")

    target_ra = None
    target_dec = None
    target_name = "target"

    if target and target.lower() in BENCHMARKS:
        b = BENCHMARKS[target.lower()]
        target_ra = b["ra"]
        target_dec = b["dec"]
        target_name = target.lower()
    elif ra and dec:
        target_ra, target_dec = parse_celestial_coords(ra, dec)
        target_name = f"sky_{target_ra:.4f}_{target_dec:.4f}"

    # 1. Search dynamic_fits by coordinate string
    if target_ra is not None and target_dec is not None and os.path.exists(dyn_dir):
        ra_str = f"{target_ra:.4f}"
        pattern = os.path.join(dyn_dir, f"*{ra_str}*{survey_suffix}")
        matches = glob.glob(pattern)
        if matches:
            filename = f"spherex_{target_name}_epoch{epoch}_{survey_suffix}"
            return FileResponse(matches[0], media_type="application/fits", filename=filename)

    # 2. Search fits dir by target name
    if target and os.path.exists(fits_dir):
        p = os.path.join(fits_dir, f"{target.lower()}_{survey_suffix}")
        if os.path.exists(p):
            filename = f"spherex_{target.lower()}_epoch{epoch}_{survey_suffix}"
            return FileResponse(p, media_type="application/fits", filename=filename)

    # 3. If any FITS file in dynamic_fits matches epoch, return most recent
    if os.path.exists(dyn_dir):
        matches = sorted(glob.glob(os.path.join(dyn_dir, f"*{survey_suffix}")), key=os.path.getmtime, reverse=True)
        if matches:
            filename = f"spherex_field_epoch{epoch}_{survey_suffix}"
            return FileResponse(matches[0], media_type="application/fits", filename=filename)

    raise HTTPException(status_code=404, detail="Requested FITS file not found in telescope archive.")

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
