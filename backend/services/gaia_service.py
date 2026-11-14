"""
🛰️ SPHEREx Hunter - Live Gaia DR3 Astrometry TAP Client
NASA Space Apps Challenge 2026 - Team RIP

Queries the official Gaia Data Release 3 (DR3) catalog directly from NASA IRSA's
TAP service using pyvo, providing authentic proper motions (pmra, pmdec),
parallax, and optical G-band magnitudes for astronomical cross-matching.
"""

import json
import os
import time

import numpy as np
import pyvo as vo

from backend.services.catalog_engine import _make_timeout_session, _safe_float
from backend.utils.validation import validate_coordinates

ESA_GAIA_TAP_URL = "https://gea.esac.esa.int/tap-server/tap"
IRSA_TAP_URL = "https://irsa.ipac.caltech.edu/TAP"

CACHE_DIR_GAIA_SVC = os.path.join(os.path.dirname(__file__), "..", "cache", "gaia_service")
os.makedirs(CACHE_DIR_GAIA_SVC, exist_ok=True)
_CATALOG_GAIA_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_gaia")

# High-speed in-memory LRU cache for Gaia cone searches
_GAIA_CACHE = {}
_MAX_GAIA_CACHE = 64


def _parse_gaia_rows(res) -> list[dict]:
    parsed = []
    for row in res:
        raw_pmra = _safe_float(row["pmra"])
        raw_pmdec = _safe_float(row["pmdec"])
        raw_plx = _safe_float(row["parallax"])
        raw_g = _safe_float(row["phot_g_mean_mag"])

        pmra_val = round(raw_pmra, 2) if raw_pmra is not None else None
        pmdec_val = round(raw_pmdec, 2) if raw_pmdec is not None else None
        plx_val = round(raw_plx, 2) if raw_plx is not None else None
        gmag_val = round(raw_g, 2) if raw_g is not None else None

        total_pm = None
        if pmra_val is not None and pmdec_val is not None:
            total_pm = float(round(np.hypot(pmra_val, pmdec_val), 2))

        parsed.append({
            "source_id": str(row["source_id"]),
            "ra": float(round(float(row["ra"]), 5)),
            "dec": float(round(float(row["dec"]), 5)),
            "pm_ra_mas_yr": pmra_val,
            "pm_dec_mas_yr": pmdec_val,
            "total_pm_mas_yr": total_pm,
            "parallax_mas": plx_val,
            "phot_g_mag": gmag_val,
        })
    return parsed


def query_gaia_dr3(ra: float, dec: float, radius_arcmin: float = 3.0, row_limit: int = 50) -> dict:
    """
    Executes an astronomical ADQL cone search on Gaia DR3 via ESA Gaia TAP
    with automatic NASA IRSA `gaia_dr3_source` fallback and L1/L2 disk caching.
    """
    ra, dec, radius_arcmin = validate_coordinates(ra, dec, radius_arcmin)
    t0 = time.time()
    cache_key = f"{round(ra, 4)}_{round(dec, 4)}_{round(radius_arcmin, 1)}"
    disk_key = f"{ra:.4f}_{dec:.4f}_{float(radius_arcmin):.1f}".replace("+", "").replace("-", "m")
    disk_cache_path = os.path.join(CACHE_DIR_GAIA_SVC, f"gaia_svc_{disk_key}.json")

    # 1. Check L1 RAM Cache
    if cache_key in _GAIA_CACHE:
        cached = dict(_GAIA_CACHE[cache_key])
        cached["telemetry"] = {
            "cache_tier": "L1_RAM",
            "fetch_time_ms": round((time.time() - t0) * 1000, 2)
        }
        return cached

    # 2. Check L2 Disk Cache
    if os.path.exists(disk_cache_path):
        try:
            with open(disk_cache_path, "r", encoding="utf-8") as f:
                cached_disk = json.load(f)
            cached_disk["telemetry"] = {
                "cache_tier": "L2_DISK",
                "fetch_time_ms": round((time.time() - t0) * 1000, 2)
            }
            _GAIA_CACHE[cache_key] = cached_disk
            return cached_disk
        except Exception:
            pass

    radius_deg = float(radius_arcmin) / 60.0
    select_cols = "SELECT TOP {limit} source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag".format(limit=row_limit)
    where_clause = (
        f"WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.5f}, {dec:.5f}, {radius_deg:.5f}))\n"
        "ORDER BY phot_g_mean_mag ASC"
    )

    sources = []
    query_error = None
    archive_host = "European Space Agency (ESA Gaia TAP)"
    cache_tier = "LIVE_ESA_TAP"

    # 3. Primary: ESA Gaia TAP -> Fallback: NASA IRSA TAP -> Fallback: Local catalog_gaia cache
    try:
        esa_svc = vo.dal.TAPService(ESA_GAIA_TAP_URL, session=_make_timeout_session(6.0))
        res = esa_svc.run_sync(f"{select_cols}\nFROM gaiadr3.gaia_source\n{where_clause}")
        sources = _parse_gaia_rows(res)
    except Exception as esa_err:
        print(f"ESA Gaia TAP query failed for RA {ra}, Dec {dec}: {esa_err}")
        try:
            archive_host = "NASA/IPAC Infrared Science Archive (IRSA TAP)"
            cache_tier = "LIVE_IRSA_TAP"
            irsa_svc = vo.dal.TAPService(IRSA_TAP_URL, session=_make_timeout_session(6.0))
            res = irsa_svc.run_sync(f"{select_cols}\nFROM gaia_dr3_source\n{where_clause}")
            sources = _parse_gaia_rows(res)
        except Exception as irsa_err:
            alt_cache_path = os.path.join(_CATALOG_GAIA_CACHE_DIR, f"gaia_{disk_key}.json")
            if os.path.exists(alt_cache_path):
                try:
                    with open(alt_cache_path, "r", encoding="utf-8") as f:
                        alt_data = json.load(f)
                    for src in alt_data.get("sources", [])[:row_limit]:
                        sources.append({
                            "source_id": str(src.get("source_id", "")),
                            "ra": float(round(float(src["ra"]), 5)),
                            "dec": float(round(float(src["dec"]), 5)),
                            "pm_ra_mas_yr": src.get("pmra_mas_yr"),
                            "pm_dec_mas_yr": src.get("pmdec_mas_yr"),
                            "total_pm_mas_yr": src.get("total_pm_mas_yr"),
                            "parallax_mas": src.get("parallax_mas"),
                            "phot_g_mag": src.get("g_mag"),
                        })
                    archive_host = "Local Catalog Cache (catalog_gaia)"
                    cache_tier = "L2_CATALOG_CACHE"
                except Exception:
                    sources = []
            if not sources:
                print(f"Gaia DR3 TAP query failed on all mirrors for RA {ra}, Dec {dec}: {irsa_err}")
                query_error = f"ESA: {esa_err}; IRSA: {irsa_err}"

    elapsed_ms = round((time.time() - t0) * 1000, 2)

    result = {
        "status": "unavailable" if query_error else "success",
        "message": f"Gaia DR3 TAP unreachable: {query_error}" if query_error else None,
        "catalog": "Gaia Data Release 3 (Gaia DR3)",
        "archive_host": archive_host,
        "search_center": {
            "ra_deg": ra,
            "dec_deg": dec,
            "radius_arcmin": radius_arcmin
        },
        "matched_count": len(sources),
        "sources": sources,
        "telemetry": {
            "cache_tier": cache_tier,
            "fetch_time_ms": elapsed_ms
        }
    }

    if query_error:
        return result  # never cache a failed query

    # Store in L1 RAM and L2 Disk caches
    if len(_GAIA_CACHE) >= _MAX_GAIA_CACHE:
        del _GAIA_CACHE[next(iter(_GAIA_CACHE))]
    _GAIA_CACHE[cache_key] = result
    try:
        with open(disk_cache_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except Exception:
        pass

    return result
