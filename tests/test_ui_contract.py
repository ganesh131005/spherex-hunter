"""
🏛️ SPHEREx Hunter - Frontend UI & Headless DOM Contract Test Suite
Validates strict codebase criteria for GitHub Issues:
- Issue #19: Dark / Light Observatory Theme Switching & FITS Invariance
- Issue #20: Actionable User-Friendly Error Messages & Retry Controls
- Issue #21: Previous Analyses / My Investigations Session Persistence
- Issue #22: Save Analysis Session Snapshot, CRUD, & Toast Notifications
- Issue #24: 4-Epoch Flipbook VCR Cycle
- Issue #27 / #31: Collision-Proof Bottom HUD, 36px Compass Rose, Dynamic Scale Bar
- Issue #29: Pinned Non-Scrolling Left Tool Rail
- Issue #30: Client IndexedDB Texture Storage & 85% Capacity LRU Eviction
"""

import os

import pytest

pytest.importorskip("bs4")
from bs4 import BeautifulSoup

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")


def _get_html_and_soup():
    assert os.path.exists(INDEX_PATH), f"Frontend file missing: {INDEX_PATH}"
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    return html, soup


def test_issue_19_theme_switching_contract():
    """Validates Issue #19: Theme switcher button, CSS rules, FITS canvas invariance, and localStorage."""
    html, soup = _get_html_and_soup()

    # 1. Theme toggle button in header
    btn_theme = soup.find(id="btnThemeToggle")
    assert btn_theme is not None, "Missing #btnThemeToggle button in header"
    assert "themeToggleIcon" in str(btn_theme) or btn_theme.find(id="themeToggleIcon") is not None

    # 2. CSS theme-light classes exist
    assert "body.theme-light" in html, "Missing body.theme-light CSS palette definitions"

    # 3. Critical FITS Invariance: Viewport, AstroCanvas, and Aladin must NOT be inverted
    assert "body.theme-light #viewportContainer" in html, "Missing FITS invariance CSS for #viewportContainer"
    assert "body.theme-light #astroCanvas" in html, "Missing FITS invariance CSS for #astroCanvas"
    assert "body.theme-light #aladinContainer" in html, "Missing FITS invariance CSS for #aladinContainer"

    # 4. JavaScript functions & LocalStorage persistence
    assert "spherex_theme" in html, "Missing 'spherex_theme' localStorage key"
    assert "setObservatoryTheme" in html, "Missing setObservatoryTheme() function"


def test_issue_20_friendly_error_banner_and_retry_contract():
    """Validates Issue #20: Plain-language error banners, contextual formatters, and retry controls."""
    html, soup = _get_html_and_soup()

    # 1. Actionable Error Banner container
    banner = soup.find(id="friendlyErrorBanner")
    assert banner is not None, "Missing #friendlyErrorBanner container"
    assert soup.find(id="friendlyErrorTitle") is not None, "Missing #friendlyErrorTitle"
    assert soup.find(id="friendlyErrorExplanation") is not None, "Missing #friendlyErrorExplanation"
    assert soup.find(id="friendlyErrorRemediation") is not None, "Missing #friendlyErrorRemediation"

    # 2. Interactive action buttons
    assert soup.find(id="btnFriendlyErrorRetry") is not None, "Missing #btnFriendlyErrorRetry (Retry Fetch)"
    assert soup.find(id="btnFriendlyErrorSafe") is not None, "Missing #btnFriendlyErrorSafe (Return to Safe Preset)"
    assert soup.find(id="btnFriendlyErrorClose") is not None, "Missing #btnFriendlyErrorClose"

    # 3. JavaScript formatters & scenario coverage
    assert "formatFriendlyError" in html, "Missing formatFriendlyError() logic"
    assert "showFriendlyErrorBanner" in html, "Missing showFriendlyErrorBanner() function"
    assert "hideFriendlyErrorBanner" in html, "Missing hideFriendlyErrorBanner() function"

    # Ensure key error contexts are mapped to friendly plain English
    assert "invalid_coordinates" in html, "Missing invalid coordinates plain-English translation"
    assert "inverted_date_range" in html, "Missing inverted date range translation"
    assert "corrupted_fits_image" in html, "Missing corrupted FITS translation"


def test_issue_21_investigations_drawer_contract():
    """Validates Issue #21: Previous Analyses / My Investigations persistence, drawer modal, and stale notice."""
    html, soup = _get_html_and_soup()

    # 1. Topbar Investigations Button & Count Badge
    btn_open = soup.find(id="btnOpenInvestigations")
    assert btn_open is not None, "Missing #btnOpenInvestigations button in header"
    badge = soup.find(id="investigationsCountBadge")
    assert badge is not None, "Missing #investigationsCountBadge"

    # 2. Investigations Modal & List Container
    modal = soup.find(id="investigationsModal")
    assert modal is not None, "Missing #investigationsModal dialog"
    list_container = soup.find(id="investigationsListContainer")
    assert list_container is not None, "Missing #investigationsListContainer"

    # 3. LocalStorage persistence key & state restoration
    assert "spherex_saved_investigations" in html, "Missing 'spherex_saved_investigations' localStorage key"
    assert "restoreInvestigationSession" in html, "Missing restoreInvestigationSession() function"
    assert "Fetch Updated Data" in html, "Missing 'Fetch Updated Data' 1-click stale refresh action"


def test_issue_22_save_analysis_and_crud_contract():
    """Validates Issue #22: 'Save Analysis' button, session naming inputs, full CRUD, and confirmation toasts."""
    html, soup = _get_html_and_soup()

    # 1. Topbar 'Save Analysis' Button
    btn_save = soup.find(id="btnSaveAnalysis")
    assert btn_save is not None, "Missing #btnSaveAnalysis button in header"

    # 2. Session Naming & Notes Inputs
    inp_name = soup.find(id="sessionNameInput")
    assert inp_name is not None, "Missing #sessionNameInput for session naming"
    inp_notes = soup.find(id="sessionNotesInput")
    assert inp_notes is not None, "Missing #sessionNotesInput for candidate notes"

    # 3. Confirm Save & Update Buttons
    assert soup.find(id="btnConfirmSaveSession") is not None, "Missing #btnConfirmSaveSession"
    assert soup.find(id="btnUpdateSelectedSession") is not None, "Missing #btnUpdateSelectedSession"

    # 4. CRUD operations in JavaScript
    assert "saveAnalysisSession" in html, "Missing saveAnalysisSession() function"
    assert "updateInvestigationSession" in html, "Missing updateInvestigationSession() function"
    assert "renameInvestigationSession" in html, "Missing renameInvestigationSession() function"
    assert "deleteInvestigationSession" in html, "Missing deleteInvestigationSession() function"

    # 5. Toast notification container
    assert soup.find(id="toastContainer") is not None, "Missing #toastContainer for confirmation toasts"
    assert "Session saved successfully!" in html, "Missing 'Session saved successfully!' toast message"


def test_issues_24_27_29_30_components_contract():
    """Validates Issues #24 (Flipbook), #27/#31 (HUD/Compass), #29 (Tool Rail), and #30 (LRU Cache)."""
    html, soup = _get_html_and_soup()

    # Issue #24: 4-epoch blink flipbook VCR
    assert soup.find(id="toolBlinkFlip") is not None, "Missing #toolBlinkFlip"
    assert "getTotalEpochCount" in html, "Missing getTotalEpochCount() for 4-epoch flipbook"

    # Issue #27 / #31: 36px Compass Rose & Dynamic Scale Bar
    compass = soup.find(id="celestialCompassRose")
    assert compass is not None, "Missing #celestialCompassRose element"
    assert "w-9 h-9" in str(compass), "#celestialCompassRose must be 36px (w-9 h-9)"
    assert soup.find(id="vpScaleBarLine") is not None, "Missing #vpScaleBarLine"
    assert soup.find(id="vpScaleBarLabel") is not None, "Missing #vpScaleBarLabel"

    # Issue #29: Left Tool Rail primary buttons
    rail = soup.find(id="leftToolRail")
    assert rail is not None, "Missing #leftToolRail aside"
    for tool_id in ["toolSelect", "toolPan", "toolMeasure", "toolBlinkFlip", "toggleGaia", "toolRecenter", "toolResetZoom", "toolWalk", "toolFullscreen", "toolMute"]:
        assert soup.find(id=tool_id) is not None, f"Missing #{tool_id} in left tool rail"

    # Issue #30: IndexedDB texture cache with capacity threshold
    assert "spherex_tile_store" in html, "Missing 'spherex_tile_store' IndexedDB"
    assert "capacityThreshold" in html, "Missing capacityThreshold calculation in pruneClientCacheIfNeeded"
    assert "fetchWithCancellation" in html, "Missing fetchWithCancellation() for in-flight AbortController"


def test_issue_32_header_responsive_contract():
    """Validates Issue #32: Header responsive layout, benchmark presets accessibility, and overflow dropdown."""
    html, soup = _get_html_and_soup()

    # 1. Benchmark target presets exist and have .target-btn class
    target_btns = soup.find_all("button", class_="target-btn")
    assert len(target_btns) >= 5, f"Expected at least 5 benchmark .target-btn buttons, found {len(target_btns)}"
    targets_present = {b.get("data-target") for b in target_btns}
    assert "wise0855" in targets_present, "WISE 0855 preset missing"
    assert "barnard" in targets_present, "Barnard's Star preset missing"
    assert "epsindi" in targets_present, "Eps Indi B preset missing"

    # 2. Responsive overflow menu exists for standard and narrow desktop widths
    assert soup.find(id="btnHeaderMoreActions") is not None, "Missing #btnHeaderMoreActions overflow trigger"
    assert soup.find(id="headerMoreActionsDropdown") is not None, "Missing #headerMoreActionsDropdown menu"

    # 3. All essential observatory controls exist in DOM with IDs
    for req_id in [
        "btnSaveAnalysis", "btnOpenInvestigations", "btnThemeToggle",
        "btnOpenOnboarding", "btnToggleUserMode", "btnOpenValidation",
        "btnOpenShortcuts", "toggleSidebarBtn", "btnTopFetch", "btnAiCopilot"
    ]:
        assert soup.find(id=req_id) is not None, f"Required control #{req_id} missing from header DOM"


def test_issue_35_byok_gemini_contract():
    """Validates Issue #35: BYOK Gemini settings modal, localStorage persistence, and live AI integration."""
    html, soup = _get_html_and_soup()

    # 1. BYOK Settings Modal elements
    assert soup.find(id="byokSettingsModal") is not None, "Missing #byokSettingsModal modal"
    assert soup.find(id="inputGeminiApiKey") is not None, "Missing #inputGeminiApiKey password input"
    assert soup.find(id="btnSaveApiKey") is not None, "Missing #btnSaveApiKey button"
    assert soup.find(id="btnClearApiKey") is not None, "Missing #btnClearApiKey button"
    assert soup.find(id="btnOpenByokSettings") is not None, "Missing #btnOpenByokSettings button in AI modal"

    # 2. LocalStorage and BYOK JavaScript functions
    assert "spherex_gemini_api_key" in html, "Missing 'spherex_gemini_api_key' localStorage key"
    assert "updateByokStatus" in html, "Missing updateByokStatus() function"
    assert "X-Gemini-Key" in html, "Missing X-Gemini-Key header dispatch in askAiCopilot"

    # 3. Backend endpoint accepts api_key and returns valid schema
    from fastapi.testclient import TestClient

    from backend.main import app
    client = TestClient(app)
    r = client.post("/api/ai/ask", json={
        "ra": 133.79513,
        "dec": -7.24515,
        "fov": 3.0,
        "target": "wise0855",
        "question": "Is this object moving?",
        "api_key": "test_byok_dummy_key_12345678"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "answer" in data
    assert "evidence_tier" in data


def test_issue_36_cursor_popover_and_spectrum_contract():
    """Validates Issue #36: High-contrast celestial cursor, coordinate popover bounds, and curve-pinned molecular diamonds."""
    html, soup = _get_html_and_soup()

    # 1. High-contrast celestial SVG cursor in CSS
    assert "celestial-cursor" in html, "Missing .celestial-cursor CSS definition"
    assert "url(\"data:image/svg+xml" in html, "Missing SVG reticle cursor definition"

    # 2. Coordinate popover container with responsive max-width boundary
    popover = soup.find(id="coordsPopover")
    assert popover is not None, "Missing #coordsPopover element"
    assert "max-w-" in str(popover), "#coordsPopover must contain responsive max-width constraint"

    # 3. 102-band spectrum molecular markers interpolate SED curve Y-position
    assert "chart.scales.y.getPixelForValue" in html, "Molecular diamonds must query chart.scales.y.getPixelForValue on the SED curve"
    assert "MOLECULAR_ANNOTATIONS.forEach" in html, "Missing MOLECULAR_ANNOTATIONS rendering loop"


def test_issue_37_aladin_real_survey_contract():
    """Validates Issue #37: Reliable real 2MASS all-sky base survey eliminating black void."""
    html, soup = _get_html_and_soup()

    # 1. Primary online survey is set to real 2MASS all-sky color HiPS
    assert "ONLINE_SURVEY = 'P/2MASS/color'" in html, "ONLINE_SURVEY must be 'P/2MASS/color'"
    assert "FALLBACK_SURVEY = '/app/P/DSS2/color'" in html, "FALLBACK_SURVEY must be local '/app/P/DSS2/color'"

    # 2. Status badge indicates 2MASS All-Sky IR
    assert "2MASS All-Sky IR (Online)" in html, "Missing '2MASS All-Sky IR (Online)' status badge label"
    assert "spherex_allsky_cube" not in html, "Broken 3D data cube HiPS URL must be removed from active base surveys"


def test_viewport_overhaul_v2_contract():
    """Validates Master Engineering Specification v2: Interactive Zoom Bar, Dual Scale Thresholds, and Scoped Caching."""
    import json
    html, soup = _get_html_and_soup()

    # 1. Interactive Zoom Bar container & ARIA accessibility
    zoom_bar = soup.find(id="viewportZoomBar")
    assert zoom_bar is not None, "Missing #viewportZoomBar container"
    assert soup.find(id="btnVpZoomIn") is not None, "Missing #btnVpZoomIn button"
    assert soup.find(id="btnVpZoomOut") is not None, "Missing #btnVpZoomOut button"
    assert soup.find(id="btnVpZoomReset") is not None, "Missing #btnVpZoomReset button"
    assert soup.find(id="btnToggleNativePixels") is not None, "Missing #btnToggleNativePixels button"

    slider = soup.find(id="vpZoomSlider")
    assert slider is not None, "Missing #vpZoomSlider"
    assert slider.get("role") == "slider", "Slider must have role='slider'"
    assert slider.get("aria-orientation") == "vertical"
    assert float(slider.get("min")) == 0.4
    assert float(slider.get("max")) == 8.0

    # 2. Dual Scale Thresholds Tooltip & Telemetry in HUD
    tooltip = soup.find(id="vpZoomTooltip")
    assert tooltip is not None, "Missing #vpZoomTooltip container"
    assert "12.9″/px" in str(tooltip), "HiPS native scale indicator (12.9″/px) missing in tooltip"
    assert "6.15″/px" in str(tooltip), "Exposure native scale indicator (6.15″/px) missing in tooltip"

    assert soup.find(id="vpDeviceScale") is not None, "Missing #vpDeviceScale readout in HUD"
    assert soup.find(id="vpNativeSpan") is not None, "Missing #vpNativeSpan readout in HUD"
    assert soup.find(id="vpScaleStatusBadge") is not None, "Missing #vpScaleStatusBadge in HUD"
    assert "NASA/JPL/IPAC" in html, "Visible NASA/JPL/IPAC attribution missing in viewport HUD"

    # 3. JavaScript Logic: isNativePixelsMode and initViewportZoomBar exist
    assert "isNativePixelsMode" in html, "Missing isNativePixelsMode state flag"
    assert "initViewportZoomBar" in html, "Missing initViewportZoomBar initialization"
    assert "cacheTelemetry" in html, "Missing window.cacheTelemetry counters"

    # 4. Deterministic 102-channel table generated and valid
    channels_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data", "spherex_102_channels.json")
    assert os.path.exists(channels_path), f"Missing generated channel file: {channels_path}"
    with open(channels_path, "r", encoding="utf-8") as f:
        ch_data = json.load(f)
    assert ch_data["total_channels"] == 102
    assert len(ch_data["channels"]) == 102
    assert ch_data["channels"][-1]["resolving_power"] == 128

    # 5. Gaia Space Motion & Residuals Engine exists
    from backend.services.gaia_service import compute_astrometric_residuals, propagate_gaia_sources_to_epoch
    res = propagate_gaia_sources_to_epoch(
        [{"ra": 133.795, "dec": -7.245, "pm_ra_mas_yr": 100.0, "pm_dec_mas_yr": -50.0, "parallax_mas": 10.0}],
        target_mjd=60800.0
    )
    assert len(res) == 1
    assert "ra_propagated" in res[0]
    residuals = compute_astrometric_residuals(None, res)
    assert residuals["status"] == "ok"
    assert "median_offset_arcsec" in residuals
