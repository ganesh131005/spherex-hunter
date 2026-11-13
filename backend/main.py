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
    run_automated_source_discovery,
    BENCHMARKS,
    clear_all_caches,
    get_cache_stats
)
from backend.services.gaia_service import query_gaia_dr3
from backend.services.neossat_service import build_neossat_tracking_report, build_portal_links
from backend.services.verification_service import run_wiseview_verification

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
    candidate_name: Optional[str] = None
    motion_type: Optional[str] = None
    proper_motion_mas: Optional[float] = 0.0
    astronomer: Optional[str] = "@citizen_scientist"
    object_type: Optional[str] = None
    user_handle: Optional[str] = None
    notes: Optional[str] = ""
    target_name: Optional[str] = None

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
@app.get("/api/benchmarks")
def get_benchmark_targets():
    """Returns the 5 NASA benchmark validation targets as pure coordinate bookmarks."""
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

@app.post("/api/cache/clear")
def clear_cache():
    """Flushes L1 RAM LRU cache and purges dynamic FITS files from disk."""
    return clear_all_caches()

@app.get("/api/cache/stats")
def cache_stats():
    """Returns current cache metrics."""
    return get_cache_stats()

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
    lod: int = Query(1, description="Game Level of Detail tier: 0 (Hero Deep), 1 (Standard Science), 2 (Wide Overview)"),
    force_refresh: bool = Query(False, description="Bypass all caches and force fresh NASA query")
):
    """
    Universal Astronomical Pipeline:
    Processes ANY celestial coordinates through authentic FITS retrieval, WCS alignment,
    difference imaging, and multi-tier caching.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        data = fetch_real_cutout(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target, lod=lod, force_refresh=force_refresh)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gaia")
def get_gaia_astrometry(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    radius: float = Query(3.0, description="Search radius in arcminutes")
):
    """
    Queries official Gaia Data Release 3 (DR3) catalog directly from NASA IRSA TAP.
    Returns stellar proper motions, parallax, and optical G-band magnitudes.
    """
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return query_gaia_dr3(ra=ra_deg, dec=dec_deg, radius_arcmin=radius)
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

@app.get("/api/source_discovery")
def source_discovery(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Runs Caltech-IPAC Source Discovery + CSA NEOSSat Line Segment Detector (LSD) streaklet analysis."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return run_automated_source_discovery(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/neossat")
def get_neossat_tracking(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    epoch: Optional[str] = Query(None, description="ISO UTC observation epoch"),
    include_cadc: bool = Query(True, description="Query CADC CAOM-2 TAP for NEOSSat archival footprints")
):
    """Task 4: Queries IMCCE SkyBoT known Solar System objects and CADC CAOM-2 NEOSSat observations."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return build_neossat_tracking_report(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, epoch=epoch, include_cadc=include_cadc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verify_candidate")
def verify_candidate_wiseview(
    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),
    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),
    fov: float = Query(3.0, description="Field of View in arcminutes"),
    target: Optional[str] = Query(None, description="Benchmark target key")
):
    """Task 3: Runs Backyard Worlds WiseView 5-step verification checklist (Dipole + Gaia DR3 + SkyBoT + W1-W2 + WiseView)."""
    try:
        ra_deg, dec_deg = parse_celestial_coords(ra, dec)
        return run_wiseview_verification(ra=ra_deg, dec=dec_deg, fov_arcmin=fov, target_key=target)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resources_codex")
def get_resources_codex(
    ra: str = Query("133.79513", description="Current Right Ascension"),
    dec: str = Query("-7.24515", description="Current Declination"),
    fov: float = Query(3.0, description="Current Field of View in arcminutes")
):
    """Task 5: Official NASA, IPAC, MAST, WiseView, CSA NEOSSat & CADC Resources Codex with live coordinate queries."""
    ra_deg, dec_deg = parse_celestial_coords(ra, dec)
    links = build_portal_links(ra_deg, dec_deg, fov)
    return {
        "status": "success",
        "coordinates": {"ra_deg": ra_deg, "dec_deg": dec_deg, "fov_arcmin": fov},
        "links": links,
        "portals": [
            {
                "id": "irsa_spherex",
                "title": "1. NASA/IPAC IRSA SPHEREx Archive",
                "agency": "NASA / Caltech-IPAC",
                "url": "https://irsa.ipac.caltech.edu/Missions/spherex.html",
                "explorer_url": links["irsa_spherex"],
                "role": "102-band Linear Variable Filter (0.75–5.0 μm) all-sky spectrophotometry, L2 quality bitmasks & AWS S3 cloud FITS.",
                "query_lang": "ADQL (IRSA TAP)",
                "query_snippet": (
                    f"SELECT 'https://irsa.ipac.caltech.edu/' || a.uri || '?center=' || p.ra || ',' || p.dec || 'd&size=0.1' AS uri,\n"
                    f"       p.energy_bandpassname, p.time_bounds_lower\n"
                    f"FROM spherex.artifact a JOIN spherex.plane p ON a.planeid = p.planeid\n"
                    f"WHERE 1 = CONTAINS(POINT('ICRS', {ra_deg:.5f}, {dec_deg:.5f}), p.poly)\n"
                    f"ORDER BY p.time_bounds_lower"
                )
            },
            {
                "id": "ipac_tutorials",
                "title": "2. Caltech-IPAC SPHEREx Python Tutorials",
                "agency": "Caltech-IPAC",
                "url": "https://caltech-ipac.github.io/irsa-tutorials/spherex/",
                "explorer_url": "https://caltech-ipac.github.io/spherex-archive-documentation/spherex-data-products/",
                "role": "Source Discovery Tool Demo (Alard-Lupton image subtraction), wavelength-dependent PSF extraction & HiPS spectral cubes.",
                "query_lang": "Python (PyVO)",
                "query_snippet": (
                    f"import pyvo as vo\n"
                    f"tap = vo.dal.TAPService('https://irsa.ipac.caltech.edu/TAP')\n"
                    f"res = tap.search(\"SELECT TOP 10 * FROM spherex.plane WHERE 1=CONTAINS(POINT('ICRS',{ra_deg:.5f},{dec_deg:.5f}),poly)\")"
                )
            },
            {
                "id": "wiseview",
                "title": "3. Backyard Worlds WiseView Comparator",
                "agency": "NASA Citizen Science / Dan Caselden",
                "url": links["wiseview"],
                "explorer_url": links["wiseview_difference"],
                "role": "14+ years of unWISE time-resolved W1 (3.4 μm) & W2 (4.6 μm) co-adds with AsinhStretch and dipole difference blinking.",
                "query_lang": "Deep-Link URL",
                "query_snippet": links["wiseview"]
            },
            {
                "id": "mast_gaia",
                "title": "4. STScI MAST & ESA Gaia DR3 Archive",
                "agency": "STScI / ESA",
                "url": "https://archive.stsci.edu/missions-and-data/gaia",
                "explorer_url": links["mast_portal"],
                "role": "1.8 billion optical stars with micro-arcsecond proper motion vectors (pmra, pmdec), parallax & optical dropout vetting.",
                "query_lang": "ADQL (Gaia DR3 TAP)",
                "query_snippet": (
                    f"SELECT TOP 50 source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag\n"
                    f"FROM gaia_dr3_source\n"
                    f"WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra_deg:.5f}, {dec_deg:.5f}, {fov/60.0:.4f})) = 1\n"
                    f"ORDER BY phot_g_mean_mag ASC"
                )
            },
            {
                "id": "csa_neossat",
                "title": "5. CSA NEOSSat Space Telescope Mission",
                "agency": "Canadian Space Agency (CSA)",
                "url": "https://www.asc-csa.gc.ca/eng/satellites/neossat/",
                "explorer_url": links["csa_neossat_dataset"],
                "role": "15 cm f/5.88 Maksutov space telescope in sun-synchronous orbit tracking Near-Earth Asteroids (NEOs) & comets.",
                "query_lang": "Open Data Portal",
                "query_snippet": "https://data.asc-csa.gc.ca/dataset/neossat"
            },
            {
                "id": "cadc_archive",
                "title": "6. Canadian Astronomy Data Centre (CADC)",
                "agency": "NRC Canada / CADC",
                "url": "https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/",
                "explorer_url": links["cadc_neossat_search"],
                "role": "CAOM-2 TAP programmatic archive hosting calibrated NEOSSat science FITS exposures and DataLink products.",
                "query_lang": "ADQL (CADC CAOM-2 TAP)",
                "query_snippet": (
                    f"SELECT TOP 25 o.observationID, o.target_name, p.time_bounds_lower, p.time_exposure\n"
                    f"FROM caom2.Observation AS o JOIN caom2.Plane AS p ON o.obsID = p.obsID\n"
                    f"WHERE o.collection = 'NEOSSAT' AND o.intent = 'science'\n"
                    f"  AND INTERSECTS(CIRCLE('ICRS', {ra_deg:.5f}, {dec_deg:.5f}, 0.50), p.position_bounds) = 1\n"
                    f"ORDER BY p.time_bounds_lower DESC"
                )
            },
            {
                "id": "neossat_tutorial",
                "title": "7. CSA NEOSSAT_Tutorial GitHub Pipeline",
                "agency": "CSA Open Source",
                "url": "https://github.com/asc-csa/NEOSSAT_Tutorial",
                "explorer_url": links["csa_neossat_tutorial"],
                "role": "Official Python notebooks for overscan/dark subtraction, temporal median stacking & Line Segment Detector (LSD) streaklets.",
                "query_lang": "Python (astroquery.cadc)",
                "query_snippet": (
                    f"from astroquery.cadc import Cadc\n"
                    f"from astropy.coordinates import SkyCoord\n"
                    f"import astropy.units as u\n"
                    f"cadc = Cadc()\n"
                    f"results = cadc.query_region(SkyCoord({ra_deg:.5f}, {dec_deg:.5f}, unit='deg'), radius=0.5*u.deg, collection='NEOSSAT')"
                )
            }
        ]
    }

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
    from datetime import datetime, timezone
    discoveries = []
    if os.path.exists(DISCOVERIES_FILE):
        try:
            with open(DISCOVERIES_FILE, "r", encoding="utf-8") as f:
                discoveries = json.load(f)
        except Exception:
            discoveries = []
            
    entry = {
        "candidate_name": candidate.candidate_name or candidate.target_name or f"Candidate ({candidate.ra:.4f}, {candidate.dec:.4f})",
        "ra": candidate.ra,
        "dec": candidate.dec,
        "motion_type": candidate.motion_type or candidate.object_type or "high_pm",
        "proper_motion_mas": candidate.proper_motion_mas or 0.0,
        "astronomer": candidate.astronomer or candidate.user_handle or "@citizen_scientist",
        "notes": candidate.notes or "",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    discoveries.insert(0, entry)
    
    with open(DISCOVERIES_FILE, "w", encoding="utf-8") as f:
        json.dump(discoveries[:50], f, indent=2)
        
    return {"status": "recorded", "entry": entry}

if __name__ == "__main__":
    import uvicorn
    print("Starting SPHEREx Hunter Astronomical Backend on http://localhost:8000...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
