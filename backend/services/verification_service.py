"""
🔭 SPHEREx Hunter - WiseView 1-Click Verification Bridge (TASK-006 / Task 3)
NASA Space Apps Challenge 2026 - Team RIP

Backyard Worlds: Planet 9 volunteers confirm every candidate with the same short
checklist before reporting it. This module runs that checklist automatically against
live archives and hands the citizen scientist a one-click deep link into Dan Caselden's
WiseView (unWISE W1/W2 time-resolved co-adds, 2010 -> present) for the final visual
confirmation:

  1. Motion signature  - Alard-Lupton difference-map dipole at the field (2MASS -> SPHEREx/DSS2)
  2. Gaia DR3          - optical counterpart? (track-aware match over 2000-2026 epochs)
  3. Known SSO         - IMCCE SkyBoT: is it a catalogued asteroid / comet?
  4. Infrared colour   - W1-W2 (cold brown dwarfs / Planet X are very red, W1-W2 > +1.5 mag)
  5. WiseView          - human visual confirmation in unWISE (deep link generated here)
"""

import math
import time
from typing import Optional

from backend.services.gaia_service import query_gaia_dr3
from backend.services.neossat_service import (
    query_known_solar_system_objects,
    build_portal_links,
    angular_sep_arcsec,
)

GAIA_REF_EPOCH = 2016.0
GAIA_MATCH_RADIUS_ARCSEC = 6.0
SSO_MATCH_RADIUS_ARCSEC = 20.0


def _point_to_track_distance_arcsec(ra: float, dec: float, src: dict,
                                    epoch_start: float = 2000.0, epoch_end: float = 2026.5) -> float:
    """
    Minimum separation between (ra, dec) and the straight proper-motion track of a Gaia
    source between two epochs. High proper motion stars (Barnard's Star moves ~10"/yr)
    would otherwise fail a naive positional match against 2MASS-era coordinates.
    """
    pmra = src.get("pm_ra_mas_yr") or 0.0
    pmdec = src.get("pm_dec_mas_yr") or 0.0
    cos_d = max(1e-6, math.cos(math.radians(src["dec"])))

    def pos(epoch: float):
        dt = epoch - GAIA_REF_EPOCH
        return (src["ra"] + (pmra * dt / 3.6e6) / cos_d, src["dec"] + pmdec * dt / 3.6e6)

    a, b = pos(epoch_start), pos(epoch_end)
    # Local tangent-plane coordinates (arcsec) centred on the query point
    def xy(p):
        return ((p[0] - ra) * math.cos(math.radians(dec)) * 3600.0, (p[1] - dec) * 3600.0)

    ax, ay = xy(a)
    bx, by = xy(b)
    dx, dy = bx - ax, by - ay
    seg2 = dx * dx + dy * dy
    t = 0.0 if seg2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / seg2))
    return math.hypot(ax + t * dx, ay + t * dy)


def _parse_w1w2(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    try:
        return float(str(text).split()[0].replace("+", ""))
    except Exception:
        return None


def run_wiseview_verification(ra: float, dec: float, fov_arcmin: float = 3.0,
                              target_key: Optional[str] = None,
                              field_ra: Optional[float] = None, field_dec: Optional[float] = None,
                              lod: int = 1, epoch: Optional[str] = None) -> dict:
    """Runs the automated Backyard-Worlds-style vetting checklist for a sky position."""
    t0 = time.time()
    checklist = []

    # ---------------------------------------------------------------- 1. Motion signature
    motion = {"transient_type": "UNKNOWN"}
    w1w2_text = None
    try:
        from backend.services.cutout_engine import fetch_real_cutout
        f_ra = field_ra if field_ra is not None else ra
        f_dec = field_dec if field_dec is not None else dec
        cut = fetch_real_cutout(f_ra, f_dec, fov_arcmin=fov_arcmin, target_key=target_key, lod=lod)
        motion = cut.get("motion_vector") or motion
        w1w2_text = (cut.get("telemetry") or {}).get("w1_w2_color")
        ttype = motion.get("transient_type", "STATIONARY_SKY")
        if ttype == "PROPER_MOTION_DIPOLE":
            status, evidence = "pass", (f"Paired +/- dipole in the Alard-Lupton difference map "
                                        f"(shift {motion.get('shift_arcsec')}\", confidence {motion.get('confidence')}).")
        elif ttype == "VARIABLE_FLARE":
            status, evidence = "warn", f"Isolated monopole residual (variable flux, not motion), confidence {motion.get('confidence')}."
        else:
            status, evidence = "fail", "No significant residual in the difference map (stationary field)."
    except Exception as err:
        status, evidence = "na", f"Difference map unavailable: {err}"
    checklist.append({"id": "motion", "label": "Difference-map motion dipole (2MASS → SPHEREx/DSS2)",
                      "status": status, "evidence": evidence})

    # ---------------------------------------------------------------- 2. Gaia DR3 counterpart
    gaia_match = None
    gaia = query_gaia_dr3(ra, dec, radius_arcmin=max(2.0, min(6.0, fov_arcmin)), row_limit=200)
    for src in gaia.get("sources", []):
        d = _point_to_track_distance_arcsec(ra, dec, src)
        if d <= GAIA_MATCH_RADIUS_ARCSEC and (gaia_match is None or d < gaia_match["track_distance_arcsec"]):
            gaia_match = dict(src, track_distance_arcsec=round(d, 2))
    if gaia_match:
        pm = gaia_match.get("total_pm_mas_yr") or 0.0
        checklist.append({
            "id": "gaia", "label": "Gaia DR3 optical counterpart (track-aware, 2000–2026)",
            "status": "fail" if pm < 100 else "warn",
            "evidence": (f"Gaia DR3 {gaia_match['source_id']} at {gaia_match['track_distance_arcsec']}\" "
                         f"(G={gaia_match.get('phot_g_mag')}, μ={pm/1000:.2f}\"/yr). Already catalogued optical source."),
        })
    else:
        checklist.append({
            "id": "gaia", "label": "Gaia DR3 optical counterpart (track-aware, 2000–2026)",
            "status": "pass" if gaia.get("matched_count", 0) > 0 or gaia.get("status") == "success" else "na",
            "evidence": (f"No Gaia DR3 source within {GAIA_MATCH_RADIUS_ARCSEC:.0f}\" of the position or its "
                         f"proper-motion track ({gaia.get('matched_count', 0)} field stars checked). "
                         f"Optical dropout → infrared-only object."),
        })

    # ---------------------------------------------------------------- 3. Known Solar System object
    sso = query_known_solar_system_objects(ra, dec, radius_arcmin=3.0, epoch=epoch)
    sso_match = None
    if sso.get("objects"):
        nearest = sso["objects"][0]
        if nearest["offset_arcsec"] <= SSO_MATCH_RADIUS_ARCSEC:
            sso_match = nearest
    if sso.get("status") != "success":
        checklist.append({"id": "sso", "label": "Known asteroid / comet (IMCCE SkyBoT)", "status": "na",
                          "evidence": sso.get("message") or "SkyBoT unavailable."})
    elif sso_match:
        checklist.append({"id": "sso", "label": "Known asteroid / comet (IMCCE SkyBoT)", "status": "fail",
                          "evidence": (f"Known {sso_match['object_class']} '{sso_match['name']}' "
                                       f"{sso_match['offset_arcsec']}\" away (V={sso_match['v_mag']}, "
                                       f"{sso_match['rate_total_arcsec_hr']}\"/h).")})
    else:
        checklist.append({"id": "sso", "label": "Known asteroid / comet (IMCCE SkyBoT)", "status": "pass",
                          "evidence": (f"No known SSO within {SSO_MATCH_RADIUS_ARCSEC:.0f}\" at {sso['epoch_utc']} "
                                       f"({sso['count']} known SSOs in the 3' cone).")})

    # ---------------------------------------------------------------- 4. Infrared colour
    w1w2 = _parse_w1w2(w1w2_text)
    if w1w2 is None:
        checklist.append({"id": "color", "label": "W1−W2 infrared colour (cold substellar > +1.5 mag)",
                          "status": "na", "evidence": "No catalogued W1−W2 colour for this position — measure it in WiseView."})
    else:
        checklist.append({"id": "color", "label": "W1−W2 infrared colour (cold substellar > +1.5 mag)",
                          "status": "pass" if w1w2 >= 1.5 else "fail", "evidence": f"W1−W2 = {w1w2_text}."})

    # ---------------------------------------------------------------- 5. WiseView human confirmation
    links = build_portal_links(ra, dec, fov_arcmin)
    checklist.append({"id": "wiseview", "label": "Visual confirmation in WiseView (unWISE 2010 → present)",
                      "status": "pending",
                      "evidence": "Open WiseView, blink W1+W2, and confirm the source moves consistently across all epochs."})

    # ---------------------------------------------------------------- Verdict
    is_dipole = motion.get("transient_type") == "PROPER_MOTION_DIPOLE"
    if sso_match:
        verdict, verdict_text = "KNOWN_ASTEROID", f"Known Solar System object ({sso_match['name']}). Not Planet X."
    elif gaia_match and (gaia_match.get("total_pm_mas_yr") or 0) >= 100:
        verdict, verdict_text = "KNOWN_HIGH_PM_STAR", f"Catalogued high proper-motion star (Gaia DR3 {gaia_match['source_id']})."
    elif gaia_match:
        verdict, verdict_text = "STATIC_OPTICAL_STAR", "Static optical star with a Gaia DR3 counterpart."
    elif is_dipole or (w1w2 is not None and w1w2 >= 1.5):
        verdict, verdict_text = "PLANET_X_CANDIDATE", ("Infrared-only object with no Gaia DR3 counterpart and no known "
                                                         "asteroid match. Confirm motion in WiseView, then flag it!")
    else:
        verdict, verdict_text = "INCONCLUSIVE", "No optical counterpart, but no motion signature yet. Inspect in WiseView."

    passed = sum(1 for c in checklist if c["status"] == "pass")
    scored = sum(1 for c in checklist if c["status"] in ("pass", "fail", "warn"))

    return {
        "status": "success",
        "coordinates": {"ra_deg": round(ra, 6), "dec_deg": round(dec, 6), "fov_arcmin": fov_arcmin},
        "verdict": verdict,
        "verdict_text": verdict_text,
        "score": {"passed": passed, "scored": scored},
        "checklist": checklist,
        "gaia_match": gaia_match,
        "sso_match": sso_match,
        "motion_vector": motion,
        "wiseview_url": links["wiseview"],
        "links": links,
        "telemetry": {"fetch_time_ms": round((time.time() - t0) * 1000, 2),
                      "separation_test_arcsec": round(angular_sep_arcsec(ra, dec, ra, dec), 3)},
    }
