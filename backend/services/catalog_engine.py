"""
⭐ SPHEREx Hunter - Gaia DR3 Astrometric Catalog Engine
NASA Space Apps 2026 - Team RIP (darkodu)

Queries the official European Space Agency (ESA) Gaia DR3 catalog via TAP:
- Precise astrometric positions (ICRS J2016.0)
- Multi-band photometry (G, BP, RP, BP-RP color)
- Proper motion vectors (pmRA, pmDEC, total PM in mas/yr, position angle)
- Parallax & calculated stellar distance (parsecs)
- Live archive queries only. When an archive is unreachable the response says so (status 'unavailable');
  no catalogue rows are ever curated, synthesized or randomly generated.
"""

import json
import os

import numpy as np

from backend.utils.validation import validate_coordinates

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_gaia")
os.makedirs(CACHE_DIR, exist_ok=True)

def query_gaia_dr3(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0,
    limit: int = 100
) -> dict:
    """
    Queries ESA Gaia DR3 via Virtual Observatory TAP for stars within radius_arcmin of (ra, dec).
    Returns astrometric positions, proper motion vectors, parallax distances, and magnitudes.
    """
    ra, dec, radius_arcmin = validate_coordinates(ra, dec, radius_arcmin)
    radius_arcmin = float(np.clip(radius_arcmin, 0.2, 15.0))
    radius_deg = radius_arcmin / 60.0
    limit = int(np.clip(limit, 1, 300))

    cache_key = f"gaia_{ra:.4f}_{dec:.4f}_{radius_arcmin:.1f}".replace("+", "").replace("-", "m")
    cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")

    # 1. Check disk cache
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["cached"] = True
                return cached_data
        except Exception:
            pass

    sources = []
    query_error = None

    # 2. Query ESA Gaia TAP service
    try:
        import pyvo
        service = pyvo.dal.TAPService("https://gea.esac.esa.int/tap-server/tap")
        query = f"""
        SELECT TOP {limit}
            source_id, ra, dec,
            pmra, pmdec, pmra_error, pmdec_error,
            parallax, parallax_error,
            phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, bp_rp,
            radial_velocity
        FROM gaiadr3.gaia_source
        WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.5f}, {dec:.5f}, {radius_deg:.5f}))
        ORDER BY phot_g_mean_mag ASC
        """
        results = service.search(query, timeout=4.0)

        for row in results:
            src_id = str(row["source_id"])
            s_ra = float(row["ra"]) if row["ra"] is not None and not np.isnan(row["ra"]) else ra
            s_dec = float(row["dec"]) if row["dec"] is not None and not np.isnan(row["dec"]) else dec

            pmra = float(row["pmra"]) if row["pmra"] is not None and not np.isnan(row["pmra"]) else 0.0
            pmdec = float(row["pmdec"]) if row["pmdec"] is not None and not np.isnan(row["pmdec"]) else 0.0
            total_pm = float(round(np.hypot(pmra, pmdec), 2))

            # Position angle: 0 = North, 90 = East, 180 = South, 270 = West
            pm_angle = float(round(np.degrees(np.arctan2(pmra, pmdec)) % 360.0, 2)) if total_pm > 0 else 0.0

            plx = float(row["parallax"]) if row["parallax"] is not None and not np.isnan(row["parallax"]) else None
            dist_pc = float(round(1000.0 / plx, 2)) if plx is not None and plx > 0.1 else None

            g_mag = float(round(row["phot_g_mean_mag"], 2)) if row["phot_g_mean_mag"] is not None and not np.isnan(row["phot_g_mean_mag"]) else None
            bp_mag = float(round(row["phot_bp_mean_mag"], 2)) if row["phot_bp_mean_mag"] is not None and not np.isnan(row["phot_bp_mean_mag"]) else None
            rp_mag = float(round(row["phot_rp_mean_mag"], 2)) if row["phot_rp_mean_mag"] is not None and not np.isnan(row["phot_rp_mean_mag"]) else None
            bp_rp = float(round(row["bp_rp"], 2)) if row["bp_rp"] is not None and not np.isnan(row["bp_rp"]) else None

            rv = float(round(row["radial_velocity"], 2)) if row["radial_velocity"] is not None and not np.isnan(row["radial_velocity"]) else None

            # Offset from field center in arcseconds
            dx_arcsec = float(round((s_ra - ra) * np.cos(np.radians(dec)) * 3600.0, 2))
            dy_arcsec = float(round((s_dec - dec) * 3600.0, 2))

            sources.append({
                "source_id": src_id,
                "ra": s_ra,
                "dec": s_dec,
                "g_mag": g_mag,
                "bp_mag": bp_mag,
                "rp_mag": rp_mag,
                "bp_rp": bp_rp,
                "pmra_mas_yr": pmra,
                "pmdec_mas_yr": pmdec,
                "total_pm_mas_yr": total_pm,
                "pm_angle_deg": pm_angle,
                "parallax_mas": plx,
                "distance_pc": dist_pc,
                "radial_velocity_kms": rv,
                "is_high_proper_motion": total_pm > 50.0,
                "offset_arcsec": {"dx": dx_arcsec, "dy": dy_arcsec}
            })

    except Exception as e:
        query_error = str(e)
        print(f"ESA Gaia TAP query failed for ({ra}, {dec}): {e}")

    high_pm_count = sum(1 for s in sources if s.get("is_high_proper_motion", False))

    response_payload = {
        "status": "unavailable" if query_error else "success",
        "message": f"ESA Gaia TAP unreachable: {query_error}" if query_error else None,
        "cached": False,
        "query": {
            "center_ra": ra,
            "center_dec": dec,
            "radius_arcmin": radius_arcmin,
            "catalog": "Gaia DR3 (European Space Agency / ICRS J2016.0)"
        },
        "total_sources": len(sources),
        "high_proper_motion_count": high_pm_count,
        "sources": sources
    }

    if query_error:
        return response_payload  # never cache a failed query

    # Cache payload
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(response_payload, f, indent=2)
    except Exception:
        pass

    return response_payload



# =====================================================================
# 2MASS Point Source Catalog (NASA IRSA Caltech)
# =====================================================================

CACHE_DIR_2MASS = os.path.join(os.path.dirname(__file__), "..", "cache", "catalog_2mass")
os.makedirs(CACHE_DIR_2MASS, exist_ok=True)

def query_2mass_psc(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0,
    limit: int = 50
) -> dict:
    """
    Queries NASA IRSA 2MASS Point Source Catalog (fp_psc) for near-infrared J, H, Ks photometry.
    Calculates J-H, H-K, and J-K color indices with photometric quality flags.
    """
    ra, dec, radius_arcmin = validate_coordinates(ra, dec, radius_arcmin)
    radius_arcmin = float(np.clip(radius_arcmin, 0.2, 15.0))
    radius_deg = radius_arcmin / 60.0
    limit = int(np.clip(limit, 1, 200))

    cache_key = f"2mass_{ra:.4f}_{dec:.4f}_{radius_arcmin:.1f}".replace("+", "").replace("-", "m")
    cache_path = os.path.join(CACHE_DIR_2MASS, f"{cache_key}.json")

    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["cached"] = True
                return cached_data
        except Exception:
            pass

    sources = []
    query_error = None

    # 1. Query NASA IRSA TAP Service
    try:
        import pyvo
        tap = pyvo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")
        query = f"""
        SELECT TOP {limit}
            designation, ra, dec,
            j_m, h_m, k_m,
            j_msigcom, h_msigcom, k_msigcom,
            ph_qual
        FROM fp_psc
        WHERE CONTAINS(POINT('J2000', ra, dec), CIRCLE('J2000', {ra:.5f}, {dec:.5f}, {radius_deg:.5f})) = 1
        ORDER BY j_m ASC
        """
        results = tap.search(query, timeout=4.0)

        for row in results:
            desig = f"2MASS J{row['designation']}"
            s_ra = float(row["ra"])
            s_dec = float(row["dec"])

            j_m = float(row["j_m"]) if row["j_m"] is not None and not np.isnan(row["j_m"]) else None
            h_m = float(row["h_m"]) if row["h_m"] is not None and not np.isnan(row["h_m"]) else None
            k_m = float(row["k_m"]) if row["k_m"] is not None and not np.isnan(row["k_m"]) else None

            j_h = float(round(j_m - h_m, 3)) if j_m is not None and h_m is not None else None
            h_k = float(round(h_m - k_m, 3)) if h_m is not None and k_m is not None else None
            j_k = float(round(j_m - k_m, 3)) if j_m is not None and k_m is not None else None

            dx_arcsec = float(round((s_ra - ra) * np.cos(np.radians(dec)) * 3600.0, 2))
            dy_arcsec = float(round((s_dec - dec) * 3600.0, 2))

            sources.append({
                "designation": desig,
                "ra": s_ra,
                "dec": s_dec,
                "j_mag": j_m,
                "h_mag": h_m,
                "k_mag": k_m,
                "j_h": j_h,
                "h_k": h_k,
                "j_k": j_k,
                "ph_qual": str(row["ph_qual"]),
                "offset_arcsec": {"dx": dx_arcsec, "dy": dy_arcsec}
            })
    except Exception as e:
        query_error = str(e)
        print(f"NASA IRSA 2MASS TAP query failed for ({ra}, {dec}): {e}")

    response_payload = {
        "status": "unavailable" if query_error else "success",
        "message": f"NASA IRSA TAP unreachable: {query_error}" if query_error else None,
        "cached": False,
        "query": {
            "center_ra": ra,
            "center_dec": dec,
            "radius_arcmin": radius_arcmin,
            "catalog": "NASA IRSA 2MASS Point Source Catalog (fp_psc)"
        },
        "total_sources": len(sources),
        "sources": sources
    }

    if query_error:
        return response_payload  # never cache a failed query

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(response_payload, f, indent=2)
    except Exception:
        pass

    return response_payload


# =====================================================================
# SIMBAD Astronomical Object Metadata & Classification
# =====================================================================

def query_simbad_metadata(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0
) -> dict:
    """
    Live CDS SIMBAD cone search (astroquery). Returns the nearest catalogued object's
    identifier, object type, spectral type, parallax and proper motion exactly as SIMBAD
    reports them. If SIMBAD is unreachable or has no object, the status says so; nothing
    is looked up from a hardcoded table and no citation counts are invented.
    """
    out = {"query_ra": ra, "query_dec": dec, "radius_arcmin": radius_arcmin}
    try:
        import astropy.units as u
        from astropy.coordinates import SkyCoord
        from astroquery.simbad import Simbad

        tab = None
        last_err = None
        for srv in ["simbad.cds.unistra.fr", "simbad.harvard.edu"]:
            try:
                sim = Simbad()
                sim.server = srv
                sim.add_votable_fields("otype", "sp_type", "plx_value", "pmra", "pmdec")
                radius = float(np.clip(radius_arcmin, 0.1, 30.0)) * u.arcmin
                tab = sim.query_region(SkyCoord(ra * u.deg, dec * u.deg, frame="icrs"), radius=radius)
                if tab is not None:
                    break
            except Exception as e:
                last_err = e
                continue

        if tab is None:
            if last_err is not None:
                raise last_err
            out.update({"status": "no_match", "canonical_name": None, "message": "No SIMBAD object in this cone."})
            return out

        if len(tab) == 0:
            out.update({"status": "no_match", "canonical_name": None, "message": "No SIMBAD object in this cone."})
            return out

        cols = {c.lower(): c for c in tab.colnames}

        # Match nearest object by angular separation
        target_sc = SkyCoord(ra * u.deg, dec * u.deg, frame="icrs")
        ra_col = cols.get("ra")
        dec_col = cols.get("dec")
        if ra_col and dec_col:
            source_scs = SkyCoord(tab[ra_col], tab[dec_col], frame="icrs")
            seps = target_sc.separation(source_scs).arcsec
            best_idx = int(seps.argmin())
            sep_arcsec = round(float(seps[best_idx]), 3)
        else:
            best_idx = 0
            sep_arcsec = None

        def val(*names):
            for n in names:
                if n in cols:
                    v = tab[cols[n]][best_idx]
                    if v is None or (hasattr(v, "mask") and bool(v.mask)):
                        return None
                    try:
                        f = float(v)
                        return None if np.isnan(f) else f
                    except Exception:
                        t = str(v).strip()
                        return t or None
            return None

        pmra, pmdec = val("pmra"), val("pmdec")
        plx = val("plx_value", "plx")
        out.update({
            "status": "resolved",
            "canonical_name": val("main_id"),
            "simbad_id": val("main_id"),
            "object_type": val("otype"),
            "spectral_type": val("sp_type"),
            "parallax_mas": plx,
            "distance_pc": round(1000.0 / plx, 3) if plx and plx > 0 else None,
            "proper_motion_mas_yr": round(float(np.hypot(pmra, pmdec)), 2) if pmra is not None and pmdec is not None else None,
            "separation_arcsec": sep_arcsec,
            "matches_in_cone": len(tab),
            "source": "CDS SIMBAD (live)",
        })
        return out
    except Exception as e:
        out.update({"status": "unavailable", "canonical_name": None, "message": f"SIMBAD query failed: {e}"})
        return out


# =====================================================================
# Unified Multi-Survey Photometric Cross-Matching
# =====================================================================

def crossmatch_photometry(
    ra: float,
    dec: float,
    radius_arcmin: float = 3.0
) -> dict:
    """
    Performs unified multi-wavelength cross-matching across:
    - Gaia DR3 (Optical G, BP, RP + Astrometry)
    - 2MASS (Near-Infrared J, H, Ks)
    - SIMBAD (Astrophysical classification & spectral type)
    Calculates optical-to-infrared color baselines (G - Ks, BP - RP, J - Ks)
    to identify ultracold Brown Dwarfs and Planet X candidates.
    """
    gaia_res = query_gaia_dr3(ra=ra, dec=dec, radius_arcmin=radius_arcmin, limit=20)
    twomass_res = query_2mass_psc(ra=ra, dec=dec, radius_arcmin=radius_arcmin, limit=20)
    simbad_res = query_simbad_metadata(ra=ra, dec=dec, radius_arcmin=radius_arcmin)

    def _nearest(sources):
        """Nearest catalogue row to the query position (not simply the brightest)."""
        best, best_sep = {}, None
        for src in sources:
            off = src.get("offset_arcsec") or {}
            sep = float(np.hypot(off.get("dx", 0.0), off.get("dy", 0.0)))
            if best_sep is None or sep < best_sep:
                best, best_sep = src, sep
        return best

    primary_gaia = _nearest(gaia_res["sources"])
    primary_2mass = _nearest(twomass_res["sources"])
    archive_issues = [r.get("message") for r in (gaia_res, twomass_res, simbad_res)
                      if r.get("status") == "unavailable" and r.get("message")]

    g_mag = primary_gaia.get("g_mag")
    k_mag = primary_2mass.get("k_mag")
    j_mag = primary_2mass.get("j_mag")

    # Diagnostic colors
    g_k_color = float(round(g_mag - k_mag, 2)) if g_mag is not None and k_mag is not None else None
    j_k_color = float(round(j_mag - k_mag, 2)) if j_mag is not None and k_mag is not None else None

    # Planet X / Y-Dwarf Diagnostic Flag
    # Brown dwarfs are extremely red (G - Ks > 5.0 or undetectable in Gaia optical with high infrared flux)
    is_planet_x_candidate = (
        (g_k_color is not None and g_k_color > 6.0) or
        (g_mag is None and k_mag is not None) or
        ("Y4" in str(simbad_res.get("spectral_type", ""))) or
        (primary_gaia.get("total_pm_mas_yr", 0) > 1000.0)
    )

    return {
        "status": "success",
        "coordinates": {"ra": ra, "dec": dec, "radius_arcmin": radius_arcmin},
        "simbad_classification": simbad_res,
        "optical_counterpart": {
            "survey": "Gaia DR3",
            "source_id": primary_gaia.get("source_id"),
            "g_mag": g_mag,
            "bp_rp": primary_gaia.get("bp_rp"),
            "total_pm_mas_yr": primary_gaia.get("total_pm_mas_yr"),
            "distance_pc": primary_gaia.get("distance_pc")
        },
        "infrared_counterpart": {
            "survey": "NASA 2MASS PSC",
            "designation": primary_2mass.get("designation"),
            "j_mag": j_mag,
            "h_mag": primary_2mass.get("h_mag"),
            "k_mag": k_mag,
            "ph_qual": primary_2mass.get("ph_qual")
        },
        "color_diagnostics": {
            "optical_g_minus_infrared_k": g_k_color,
            "near_infrared_j_minus_k": j_k_color,
            "is_ultracold_candidate": is_planet_x_candidate,
            "classification_reason": (
                "Heuristic flag only (G-Ks > 6, no Gaia counterpart with a 2MASS detection, Y-type SIMBAD class, "
                "or Gaia proper motion > 1 arcsec/yr). Candidate, NOT confirmed."
                if is_planet_x_candidate else "No ultracold-object heuristic triggered (not a confirmation of anything)."
            )
        },
        "archive_issues": archive_issues,
        "all_gaia_sources_count": len(gaia_res["sources"]),
        "all_2mass_sources_count": len(twomass_res["sources"])
    }
