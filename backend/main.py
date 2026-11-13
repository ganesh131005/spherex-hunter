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
from backend.services.catalog_engine import (
    query_gaia_dr3,
    query_2mass_psc,
    query_simbad_metadata,
    crossmatch_photometry
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
            "/api/catalog/gaia?ra=269.45208&dec=4.69339&radius=3.0",
            "/api/catalog/2mass?ra=269.45208&dec=4.69339&radius=3.0",
            "/api/catalog/simbad?ra=269.45208&dec=4.69339",
            "/api/catalog/crossmatch?ra=269.45208&dec=4.69339",
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

@app.get("/api/catalog/gaia")
def get_gaia_catalog(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes (0.2 to 15.0)"),
    limit: int = Query(100, description="Maximum number of sources to return (1 to 300)")
):
    """
    Queries European Space Agency (ESA) Gaia DR3 catalog for astrometric sources,
    magnitudes (G, BP, RP), proper motions (pmRA, pmDEC), parallax distances, and motion vectors.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        catalog_data = query_gaia_dr3(ra=ra_deg, dec=dec_deg, radius_arcmin=radius, limit=limit)
        return catalog_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog/2mass")
def get_2mass_catalog(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes (0.2 to 15.0)"),
    limit: int = Query(50, description="Maximum number of sources to return (1 to 200)")
):
    """
    Queries NASA IRSA 2MASS Point Source Catalog (PSC) for near-infrared
    J (1.25 μm), H (1.65 μm), and Ks (2.17 μm) photometry and color indices.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return query_2mass_psc(ra=ra_deg, dec=dec_deg, radius_arcmin=radius, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog/simbad")
def get_simbad_metadata(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes")
):
    """
    Queries CDS Strasbourg SIMBAD database for canonical astronomical object identification,
    morphological and spectral classifications, and literature citation counts.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return query_simbad_metadata(ra=ra_deg, dec=dec_deg, radius_arcmin=radius)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/catalog/crossmatch")
def get_crossmatched_photometry(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes")
):
    """
    Performs unified optical-to-infrared photometric cross-matching across Gaia DR3, 2MASS,
    and SIMBAD. Computes diagnostic color baselines (G - Ks, J - Ks) to flag Brown Dwarfs and Planet X candidates.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return crossmatch_photometry(ra=ra_deg, dec=dec_deg, radius_arcmin=radius)
    except HTTPException:
        raise
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
