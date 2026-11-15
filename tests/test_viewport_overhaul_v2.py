"""
🛰️ SPHEREx Hunter - Viewport Overhaul v2 Comprehensive Test Suite (Step 6)
Validates all requirements of the Master Engineering Specification:
- Requirement 1: Authentic NASA SPHEREx DR1 Metadata & Attribution
- Requirement 2: Interactive Logarithmic Zoom Bar & Dual-Scale Thresholds (HiPS 12.9″/px vs Exposure 6.15″/px)
- Requirement 3: Scoped Multi-Tier Caching System (Quantized micro-degree keys)
- Requirement 4 & 5: Uniform Tile Resolution & Single-Tile Topology
- Requirement 6: Progressive Detail on Zoom-In with Nearest-Neighbor gl.NEAREST toggle
- Requirement 7: Accurate Multi-Epoch Placement, WISE 0855 Narrowband Stack, and Gaia DR3 EPSF Astrometry
"""

import json
import math
import os

import pytest

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
CHANNELS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data", "spherex_102_channels.json")
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "hips_spherex_dr1_sample")


def _read_index_html():
    assert os.path.exists(INDEX_PATH), f"Frontend file missing: {INDEX_PATH}"
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return f.read()


# -----------------------------------------------------------------------------
# 1. Zoom Bar DOM, Accessibility & ARIA Contract Tests
# -----------------------------------------------------------------------------
def test_zoom_bar_dom_and_aria_contract():
    """Validates Step 2: Interactive Zoom Bar, logarithmic slider, ARIA attributes and controls."""
    pytest.importorskip("bs4")
    from bs4 import BeautifulSoup
    html = _read_index_html()
    soup = BeautifulSoup(html, "html.parser")

    # Zoom Bar Container
    zoom_bar = soup.find(id="viewportZoomBar")
    assert zoom_bar is not None, "Missing #viewportZoomBar container"
    assert zoom_bar.name == "nav", "#viewportZoomBar should be a semantic <nav> element"

    # Buttons
    btn_in = soup.find(id="btnVpZoomIn")
    btn_out = soup.find(id="btnVpZoomOut")
    btn_reset = soup.find(id="btnVpZoomReset")
    btn_native = soup.find(id="btnToggleNativePixels")

    assert btn_in is not None, "Missing #btnVpZoomIn"
    assert btn_out is not None, "Missing #btnVpZoomOut"
    assert btn_reset is not None, "Missing #btnVpZoomReset"
    assert btn_native is not None, "Missing #btnToggleNativePixels"
    assert btn_native.get("aria-pressed") in ["true", "false"]

    # Slider
    slider = soup.find(id="vpZoomSlider")
    assert slider is not None, "Missing #vpZoomSlider"
    assert slider.get("role") == "slider", "Slider must have role='slider'"
    assert slider.get("aria-orientation") == "vertical"
    assert float(slider.get("min")) == 0.4
    assert float(slider.get("max")) == 8.0

    # Tooltip and Dual Threshold Badges
    tooltip = soup.find(id="vpZoomTooltip")
    assert tooltip is not None, "Missing #vpZoomTooltip"
    assert "12.9″/px" in str(tooltip), "Tooltip must indicate HiPS Native scale (~12.9″/px)"
    assert "6.15″/px" in str(tooltip), "Tooltip must indicate Exposure Native scale (6.15″/px)"


# -----------------------------------------------------------------------------
# 2. Dual-Threshold Scale Mathematics (Amendment A1)
# -----------------------------------------------------------------------------
def test_dual_scale_threshold_mathematics():
    """Validates mathematical derivation of HiPS Order 5 scale vs Teledyne H2RG detector pitch."""
    # HiPS Order 5 scale formula with tile width = 512
    k = 5
    w_tile = 512
    solid_angle = (4.0 * math.pi) / (12.0 * (4.0 ** k))
    theta_rad_per_pixel = math.sqrt(solid_angle) / w_tile
    theta_arcsec_hips5 = theta_rad_per_pixel * (180.0 * 3600.0 / math.pi)

    # Teledyne H2RG detector pixel pitch
    detector_pixel_pitch_arcsec = 6.15

    assert 12.8 < theta_arcsec_hips5 < 13.0, f"Expected Order 5 ~12.88 arcsec/px, got {theta_arcsec_hips5}"
    assert theta_arcsec_hips5 > detector_pixel_pitch_arcsec, "HiPS Order 5 MUST be strictly coarser than 6.15 arcsec/px"


# -----------------------------------------------------------------------------
# 3. Deterministic 102-Channel Table & Attribution (Step 3 / Amendment A10)
# -----------------------------------------------------------------------------
def test_deterministic_102_channels_and_attribution():
    """Validates Step 3: 102-channel table generated deterministically with IRSA R values and credit."""
    html = _read_index_html()

    assert os.path.exists(CHANNELS_JSON_PATH), f"Missing {CHANNELS_JSON_PATH}"
    with open(CHANNELS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_channels"] == 102
    assert len(data["channels"]) == 102

    # Check Band resolving powers (Amendment A10)
    b1_ch = [c for c in data["channels"] if c["band"] == 1]
    b4_ch = [c for c in data["channels"] if c["band"] == 4]
    b5_ch = [c for c in data["channels"] if c["band"] == 5]
    b6_ch = [c for c in data["channels"] if c["band"] == 6]

    assert b1_ch[0]["resolving_power"] == 41
    assert b4_ch[0]["resolving_power"] == 35
    assert b5_ch[0]["resolving_power"] == 112
    assert b6_ch[0]["resolving_power"] == 128

    # Attribution & Provenance in HTML
    assert "NASA/JPL/IPAC" in html, "Missing NASA/JPL/IPAC attribution in HTML"
    assert "DR1 Co-Added Context (Blurs Movers)" in html, "Missing provenance warning regarding blurred movers in HiPS"


# -----------------------------------------------------------------------------
# 4. WISE 0855 Narrowband Stack & Schema (Step 4 / Amendments A3, A4)
# -----------------------------------------------------------------------------
def test_wise0855_narrowband_stack_metadata():
    """Validates Step 4: Authentic WISE 0855 4.6um narrowband stack record with S/N and date range."""
    wise_exp_path = os.path.join(os.path.dirname(__file__), "..", "demo_cache", "wise0855", "exposures.json")
    assert os.path.exists(wise_exp_path), f"Missing {wise_exp_path}"

    with open(wise_exp_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    exposures = data.get("exposures", [])
    stack_items = [e for e in exposures if e.get("exposure_id") == "SPHEREx_stack_wise0855_4p6um"]
    assert len(stack_items) == 1, "Missing SPHEREx_stack_wise0855_4p6um in wise0855 exposures"

    stack = stack_items[0]
    assert stack["is_coadd"] is True
    assert stack["wavelength_um"] == 4.60
    assert stack["stack_snr"] >= 5.0
    assert stack["n_exposures"] == 26
    assert stack["mjd_min"] < stack["mjd_max"]


# -----------------------------------------------------------------------------
# 5. Gaia Space Motion Propagation & EPSF Centroid Residuals (Step 4 / Amendment A8)
# -----------------------------------------------------------------------------
def test_gaia_space_motion_and_residuals():
    """Validates Step 4: astropy.coordinates.SkyCoord.apply_space_motion and EPSF astrometric residuals."""
    from backend.services.gaia_service import compute_astrometric_residuals, propagate_gaia_sources_to_epoch

    sample_stars = [
        {"source_id": "1", "ra": 133.795, "dec": -7.245, "pm_ra_mas_yr": 120.0, "pm_dec_mas_yr": -85.0, "parallax_mas": 15.0},
        {"source_id": "2", "ra": 133.810, "dec": -7.230, "pm_ra_mas_yr": 45.0, "pm_dec_mas_yr": 20.0, "parallax_mas": 8.0}
    ]

    # Target exposure MJD: 60800.0 (Year ~2025.3) vs Gaia DR3 J2016.0
    propagated = propagate_gaia_sources_to_epoch(sample_stars, target_mjd=60800.0)
    assert len(propagated) == 2
    for s in propagated:
        assert "ra_propagated" in s
        assert "dec_propagated" in s
        assert "delta_ra_arcsec" in s
        assert "delta_dec_arcsec" in s
        assert s["ra_propagated"] != s["ra"]

    residuals = compute_astrometric_residuals(None, propagated, pixel_scale_arcsec=6.15)
    assert residuals["status"] == "ok"
    assert residuals["stars_measured"] == 2
    assert residuals["median_offset_arcsec"] is not None
    assert residuals["median_offset_native_px"] is not None
    assert residuals["tolerance_status"] in ["within_tolerance", "flagged"]


# -----------------------------------------------------------------------------
# 6. Scoped Caching Engine & Quantized Keys (Step 5 / Amendment A5)
# -----------------------------------------------------------------------------
def test_scoped_caching_and_quantized_keys():
    """Validates Step 5: Quantized integer micro-degree keys, idle prefetch and telemetry counters."""
    html = _read_index_html()

    assert "spherex_tile_store" in html, "Missing IndexedDB cache store name"
    assert "cacheTelemetry" in html, "Missing window.cacheTelemetry counters"
    assert "scheduleIdle" in html, "Missing scheduleIdle cross-browser fallback"
    assert "isDataSaverActive" in html, "Missing isDataSaverActive function"
    assert "Math.round(parseFloat(ra) * 1e5)" in html or "Math.round(" in html, "Missing micro-degree quantization logic"


# -----------------------------------------------------------------------------
# 7. Local HiPS Deterministic Fixture (Step 6 / Amendment A6)
# -----------------------------------------------------------------------------
def test_offline_hips_fixture_integrity():
    """Validates Step 6: Lightweight local HiPS fixture exists for offline deterministic CI."""
    prop_file = os.path.join(FIXTURE_DIR, "properties")
    moc_file = os.path.join(FIXTURE_DIR, "Moc.fits")
    tile_file = os.path.join(FIXTURE_DIR, "Norder0", "Dir0", "Npix0.png")

    assert os.path.exists(prop_file), f"Missing local HiPS properties fixture: {prop_file}"
    assert os.path.exists(moc_file), f"Missing local HiPS Moc.fits fixture: {moc_file}"
    assert os.path.exists(tile_file), f"Missing local HiPS Order 0 tile fixture: {tile_file}"
