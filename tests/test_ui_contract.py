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
    """Validates Issue #37 & Step 3: Authentic SPHEREx DR1 HiPS base survey and reliable local fallbacks eliminating black void."""
    html, soup = _get_html_and_soup()

    # 1. Base surveys and fallback are configured
    assert "ONLINE_SURVEY" in html, "ONLINE_SURVEY must be defined"
    assert "FALLBACK_SURVEY" in html, "FALLBACK_SURVEY must be defined"
    assert "/app/P/DSS2/color" in html, "FALLBACK_SURVEY must include local '/app/P/DSS2/color'"

    # 2. Status badge indicates HiPS readiness
    assert "DR1 HiPS Ready" in html or "2MASS All-Sky IR (Online)" in html, "Missing HiPS status badge label"


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


def test_issue_39_cutout_error_diagnostics_and_clamping_contract():
    """Validates Issue #39: Backend returns structured 400/404, clamps FOV to [1.0, 15.0], and formatFriendlyError extracts diagnostic details."""
    from fastapi.testclient import TestClient

    from backend.main import app

    client = TestClient(app)
    # 1. Backend rejects FOV > 15.0 arcmin with 400 Bad Request
    r_wide = client.get("/api/cutout?ra=133.795&dec=-7.245&fov=559.76")
    assert r_wide.status_code == 400, f"Expected HTTP 400 for FOV > 15', got {r_wide.status_code}"
    err_json = r_wide.json()
    assert "exceeds 15.0 arcmin limit" in err_json.get("detail", ""), "Detail message must explain FOV limit"

    # 2. Frontend clamps FOV to [1.0, 15.0] and extracts error detail
    html, soup = _get_html_and_soup()
    assert "Math.max(1.0, Math.min(15.0, Number(fov) || 3.0))" in html, "loadSkyCutout must clamp FOV to [1.0, 15.0]"
    assert "formatFriendlyError" in html
    assert "exceeds 15.0" in html, "formatFriendlyError must diagnose FOV limit exceedances"
    assert "Field of View Exceeds 15.0′ Limit" in html


def test_issue_40_viewport_hud_deconfliction_contract():
    """Validates Issue #40: Viewport HUD time step controller is vertically deconflicted below top telemetry and colormap controls."""
    html, soup = _get_html_and_soup()

    # 1. #viewportTimeStepHUD is placed at top-14 to avoid overlapping top telemetry and stretch row
    hud = soup.find(id="viewportTimeStepHUD")
    assert hud is not None, "Missing #viewportTimeStepHUD"
    hud_classes = hud.get("class", [])
    assert "top-14" in hud_classes, f"#viewportTimeStepHUD must be at top-14, got {hud_classes}"
    assert "top-3" not in hud_classes, "#viewportTimeStepHUD must NOT be at top-3"

    # 2. Top-left target telemetry chip (#vpTargetName) is at top-3 left-3
    vp_target = soup.find(id="vpTargetName")
    assert vp_target is not None, "Missing #vpTargetName"
    target_card = vp_target.find_parent("div", class_=lambda c: c and "top-3" in c and "left-3" in c)
    assert target_card is not None, "Top-left target card must be positioned at top-3 left-3"

    # 3. Top-right stretch controls are at top-3 right-3
    stretch_grayscale = soup.find(id="shadeGrayscale")
    assert stretch_grayscale is not None, "Missing #shadeGrayscale"
    stretch_card = stretch_grayscale.find_parent("div", class_=lambda c: c and "top-3" in c and "right-3" in c)
    assert stretch_card is not None, "Stretch controls must be positioned at top-3 right-3"

    # 4. Pop-down alert banners are deconflicted below HUD at top-28
    guided_tour = soup.find(id="guidedTourBanner")
    assert guided_tour is not None and "top-28" in guided_tour.get("class", []), "Guided tour banner must be at top-28"
    cand_alert = soup.find(id="candidateAlertStrip")
    assert cand_alert is not None and "top-28" in cand_alert.get("class", []), "Candidate alert strip must be at top-28"


def test_issue_41_typography_scale_and_readability_contract():
    """Validates Issue #41 / TASK-007: Enlarge microscopic typography to accessible scales (>=11px-14px)."""
    html, soup = _get_html_and_soup()

    # 1. #dockPanelSpectrum exists and eliminates microscopic text-[9px] and text-[10px]
    spectrum_panel = soup.find(id="dockPanelSpectrum")
    assert spectrum_panel is not None, "Missing #dockPanelSpectrum"
    spectrum_html = str(spectrum_panel)
    assert "text-[9px]" not in spectrum_html, "Microscopic text-[9px] must not exist in #dockPanelSpectrum"
    assert "text-[10px]" not in spectrum_html, "Microscopic text-[10px] must not exist in #dockPanelSpectrum"

    # 2. Wavelength stepper channel display is enlarged to text-sm font-bold min-w-[220px]
    chan_display = spectrum_panel.find(id="chanDisplay")
    assert chan_display is not None, "Missing #chanDisplay"
    cd_classes = chan_display.get("class", [])
    assert "text-sm" in cd_classes and "font-bold" in cd_classes and "min-w-[220px]" in cd_classes, (
        f"#chanDisplay must be enlarged to text-sm font-bold min-w-[220px], got {cd_classes}"
    )

    # 3. Flux badge has accessible text-xs font-mono font-bold and comfortable padding
    chan_flux = spectrum_panel.find(id="chanFluxBadge")
    assert chan_flux is not None, "Missing #chanFluxBadge"
    cf_classes = chan_flux.get("class", [])
    assert "text-xs" in cf_classes and "font-bold" in cf_classes, (
        f"#chanFluxBadge must be text-xs font-bold, got {cf_classes}"
    )

    # 4. Channel stepper buttons #chanPrev and #chanNext have comfortable touch targets w-8 h-8
    for btn_id in ["chanPrev", "chanNext"]:
        btn = spectrum_panel.find(id=btn_id)
        assert btn is not None, f"Missing #{btn_id}"
        btn_classes = btn.get("class", [])
        assert "w-8" in btn_classes and "h-8" in btn_classes, f"#{btn_id} must be w-8 h-8, got {btn_classes}"

    # 5. Non-simultaneous notice uses text-xs font-medium with comfortable padding
    notice = spectrum_panel.find(id="spectrumNonSimultaneousNotice")
    assert notice is not None, "Missing #spectrumNonSimultaneousNotice"
    notice_classes = notice.get("class", [])
    assert "text-xs" in notice_classes and "font-medium" in notice_classes, (
        f"#spectrumNonSimultaneousNotice must be text-xs font-medium, got {notice_classes}"
    )

    # 6. Molecular reference sidebar is expanded to w-64 with text-xs font-mono
    mol_sidebar = spectrum_panel.find("div", class_=lambda c: c and "w-64" in c)
    assert mol_sidebar is not None, "Molecular reference sidebar must have width w-64"
    mol_classes = mol_sidebar.get("class", [])
    assert "text-xs" in mol_classes and "font-mono" in mol_classes, (
        f"Molecular sidebar must use text-xs font-mono, got {mol_classes}"
    )

    # 7. Viewport HUD time-step controls use accessible text-xs styling
    hud = soup.find(id="viewportTimeStepHUD")
    assert hud is not None, "Missing #viewportTimeStepHUD"
    for hud_btn_id in ["btnHudStepPrev", "btnHudStepNext", "btnHudDiffMode"]:
        btn = hud.find(id=hud_btn_id)
        assert btn is not None, f"Missing #{hud_btn_id}"
        btn_classes = btn.get("class", [])
        assert "text-xs" in btn_classes, f"#{hud_btn_id} must have text-xs, got {btn_classes}"

    # 8. RA/Dec validation hints use text-xs font-mono
    ra_hint = soup.find(id="raValidationHint")
    dec_hint = soup.find(id="decValidationHint")
    assert ra_hint is not None and "text-xs" in ra_hint.get("class", []), "#raValidationHint must be text-xs"
    assert dec_hint is not None and "text-xs" in dec_hint.get("class", []), "#decValidationHint must be text-xs"


def test_issue_42_citizen_science_onboarding_redesign_contract():
    """Validates Issue #42: Redesigned snappy 3-step Cosmic Quick-Start tour, mini-blink simulation, and 15s quick start action."""
    html, soup = _get_html_and_soup()

    # 1. Onboarding modal exists with redesigned Cosmic Quick-Start branding
    modal = soup.find(id="onboardingModal")
    assert modal is not None, "Missing #onboardingModal"
    assert "Cosmic Quick-Start" in modal.get_text(), "Onboarding modal must display 'Cosmic Quick-Start' branding"

    # 2. Step badge indicates 3 snappy steps (not 5 dense textbook slides)
    step_badge = modal.find(id="onboardingStepBadge")
    assert step_badge is not None, "Missing #onboardingStepBadge"
    assert "Step" in step_badge.get_text() and "of 3" in step_badge.get_text(), (
        f"Onboarding step badge must indicate 3 steps, got '{step_badge.get_text()}'"
    )

    # 3. Step indicator dots container has exactly 3 steps
    dots_container = modal.find(id="tourDotsContainer")
    assert dots_container is not None, "Missing #tourDotsContainer"
    dots = dots_container.find_all("span")
    assert len(dots) == 3, f"Expected 3 tour indicator dots, got {len(dots)}"

    # 4. Quick Start 15s button exists in onboarding footer
    quick_start_btn = modal.find(id="btnTourQuickStart")
    assert quick_start_btn is not None, "Missing #btnTourQuickStart"
    assert "Quick Start" in quick_start_btn.get_text(), "Quick Start button must display 'Quick Start'"

    # 5. Guide trigger button exists in top navigation
    btn_open = soup.find(id="btnOpenOnboarding")
    assert btn_open is not None, "Missing #btnOpenOnboarding header trigger"

    # 6. JavaScript verifies 3-step tour configuration and interactive mini-blink simulation
    assert "const TOTAL_TOUR_STEPS = 3;" in html, "JavaScript must configure TOTAL_TOUR_STEPS = 3"
    assert "toggleMiniBlinkSimulation" in html, "JavaScript must provide toggleMiniBlinkSimulation"
    assert "launchQuickStart" in html, "JavaScript must provide launchQuickStart"
    assert "tourMiniBlinkTarget" in html, "JavaScript must provide tourMiniBlinkTarget"
    assert "tourMiniBlinkEpochLabel" in html, "JavaScript must provide tourMiniBlinkEpochLabel"
    assert "tour-slide" in html, "JavaScript must assign .tour-slide class with data-step for slide inspection"


def test_spectrum_array_a1_default_alignment_contract():
    """Validates that SPHEREx 102-Band Spectrum toolbar anchors on Array A1 by default and aligns toolbar controls."""
    html, soup = _get_html_and_soup()

    # 1. #dockPanelSpectrum exists and groups Array Tabs + Channel Stepper on the left starting with Array A1
    panel = soup.find(id="dockPanelSpectrum")
    assert panel is not None, "Missing #dockPanelSpectrum"

    array_tabs = panel.find(id="arrayTabsContainer")
    assert array_tabs is not None, "Missing #arrayTabsContainer"

    # Array A1 button has active state by default
    a1_btn = array_tabs.find("button", attrs={"data-array": "A1"})
    assert a1_btn is not None, "Missing Array A1 button"
    assert "blender-btn-active" in a1_btn.get("class", []), "Array A1 button must have blender-btn-active by default"

    # 2. Both Array Tabs and Channel Stepper are grouped together in a unified left cluster
    chan_prev = panel.find(id="chanPrev")
    assert chan_prev is not None, "Missing #chanPrev"
    parent_stepper = chan_prev.find_parent("div")
    assert parent_stepper is not None, "Missing channel stepper container"

    # Both array_tabs and parent_stepper share a common parent flex container
    common_parent = array_tabs.find_parent("div")
    assert common_parent is not None, "Missing left cluster parent container"
    assert parent_stepper in common_parent.find_all("div"), "Channel stepper must be aligned in the same cluster with arrayTabsContainer"

    # 3. JavaScript defines resetSpectrumToDefaultA1Alignment and maintains Array A1 default state
    assert "resetSpectrumToDefaultA1Alignment" in html, "Missing resetSpectrumToDefaultA1Alignment function"
    assert "window.resetSpectrumToDefaultA1Alignment" in html, "resetSpectrumToDefaultA1Alignment must be exported to window"
    assert "activeArray = 'A1'" in html, "Default activeArray must be 'A1'"
    assert "activeChannelInArray = 1" in html, "Default activeChannelInArray must be 1"


def test_merged_102_band_information_bar_in_spectrum_panel_toolbar():
    """Validates the 102-Band Information Bar is merged into the 102-Band Spectrum Toolbar in the bottom dock panel."""
    html, soup = _get_html_and_soup()

    spectrum_panel = soup.find(id="dockPanelSpectrum")
    assert spectrum_panel is not None, "Missing #dockPanelSpectrum in bottom dock"

    # 1. Merged 102-Band Information Bar exists inside the spectrum panel toolbar
    info_bar = spectrum_panel.find(id="spec102BandInfoBar")
    assert info_bar is not None, "Missing #spec102BandInfoBar in spectrum toolbar"

    # 2. Direct 102-Channel Selector and Stepper Buttons
    chan_select = info_bar.find(id="spec102ChannelSelect")
    assert chan_select is not None, "Missing #spec102ChannelSelect in merged info bar"

    btn_prev = info_bar.find(id="spec102PrevCh")
    btn_next = info_bar.find(id="spec102NextCh")
    assert btn_prev is not None and btn_next is not None, "Missing #spec102PrevCh or #spec102NextCh"

    # 3. Dedicated 102-Band Wavelength & Array Readout Display
    wl_display = info_bar.find(id="spec102WavelengthDisplay")
    assert wl_display is not None, "Missing #spec102WavelengthDisplay in merged info bar"

    # 4. Molecular Ice & Gas Feature Jump Chips in the toolbar
    mol_bar = spectrum_panel.find(id="spec102MolecularBar")
    assert mol_bar is not None, "Missing #spec102MolecularBar in spectrum toolbar"
    classes = mol_bar.get("class", [])
    assert not any("2xl:" in c for c in classes), "Molecular bar should not be restricted only to 2xl screens"
    pills = mol_bar.find_all(class_=lambda c: c and "spec-mol-pill" in c)
    assert len(pills) >= 5, f"Expected at least 5 molecular jump pills, found {len(pills)}"

    # 5. JavaScript two-way synchronization and channel dispatching
    assert "select102BandChannel" in html, "Missing select102BandChannel implementation"
    assert "window.select102BandChannel" in html, "select102BandChannel must be exported to window"
    assert "spec102ChannelSelect" in html, "JavaScript must reference spec102ChannelSelect"
    assert "spec102WavelengthDisplay" in html, "JavaScript must reference spec102WavelengthDisplay"


def test_snapblink_25_percent_increment_and_blend_timeline_alignment_contract():
    """Validates that snapblink blend rate increments by exactly 25% each frame and timeline aligns with blend toolbar."""
    html, soup = _get_html_and_soup()

    # 1. Timeline tick dots exist and are positioned at 25%, 50%, 75%, 100%
    timeline_panel = soup.find(id="dockPanelTimeline")
    assert timeline_panel is not None, "Missing #dockPanelTimeline in bottom dock"

    tick1 = timeline_panel.find(attrs={"data-frame-tick": "1"})
    tick2 = timeline_panel.find(attrs={"data-frame-tick": "2"})
    tick3 = timeline_panel.find(attrs={"data-frame-tick": "3"})
    tick4 = timeline_panel.find(attrs={"data-frame-tick": "4"})
    assert tick1 is not None and tick2 is not None and tick3 is not None and tick4 is not None, "All 4 tick dots must exist"

    # Ticks align to 25%, 50%, 75%, 100%
    assert "25%" in (tick1.get("style", "") + " " + " ".join(tick1.get("class", []))), "Tick 1 must align at 25%"
    assert "50%" in (tick2.get("style", "") + " " + " ".join(tick2.get("class", []))), "Tick 2 must align at 50%"
    assert "75%" in (tick3.get("style", "") + " " + " ".join(tick3.get("class", []))), "Tick 3 must align at 75%"
    assert "100%" in (tick4.get("style", "") + " " + " ".join(tick4.get("class", []))), "Tick 4 must align at 100%"

    # 2. Timeline progress bar exists and initializes to 25% for Frame 1
    prog = timeline_panel.find(id="timelineProgress")
    assert prog is not None, "Missing #timelineProgress"
    assert "25%" in prog.get("style", ""), "#timelineProgress must initialize to width 25%"

    # 3. Blend toolbar controls exist with 25% initial value
    blend_slider = timeline_panel.find(id="epochBlendSlider")
    blend_label = timeline_panel.find(id="epochBlendLabel")
    assert blend_slider is not None, "Missing #epochBlendSlider"
    assert blend_label is not None, "Missing #epochBlendLabel"
    assert blend_slider.get("value") == "25", "#epochBlendSlider must initialize to 25"
    assert "25%" in blend_label.get_text(), "#epochBlendLabel must initialize to 25%"

    # 4. JavaScript increments epochBlend by exact 25% increments
    assert "currentFrame * 0.25" in html, "setFlipbookFrame must increment epochBlend by exact 25% increments"
    assert "epochBlend / 0.25" in html, "Slider and loop mapping must use 25% increments"


def test_spectrum_102_horizontal_sideways_zoom_contract():
    """Validates horizontal (sideways) expansion of the 102-band spectrum via mouse wheel scroll and drag pan."""
    html, soup = _get_html_and_soup()

    # 1. Elements: Horizontal zoom bar, zoom level badge, in/out/reset buttons
    zoom_bar = soup.find(id="specHorizontalZoomBar")
    assert zoom_bar is not None, "Missing #specHorizontalZoomBar in #dockPanelSpectrum toolbar"
    assert "sideways" in zoom_bar.get("title", "").lower() or "zoom" in zoom_bar.get("title", "").lower()

    zoom_label = soup.find(id="specZoomLevelLabel")
    assert zoom_label is not None, "Missing #specZoomLevelLabel"
    assert "102 Bands" in zoom_label.get_text()

    btn_in = soup.find(id="btnSpecZoomIn")
    btn_out = soup.find(id="btnSpecZoomOut")
    btn_reset = soup.find(id="btnSpecZoomReset")
    assert btn_in is not None, "Missing #btnSpecZoomIn"
    assert btn_out is not None, "Missing #btnSpecZoomOut"
    assert btn_reset is not None, "Missing #btnSpecZoomReset"

    # 2. JavaScript Sideways Horizontal Zoom Engine
    assert "applySpectrumHorizontalZoom" in html, "Missing applySpectrumHorizontalZoom function"
    assert "zoomSpectrumHorizontalAt" in html, "Missing zoomSpectrumHorizontalAt function"
    assert "window.applySpectrumHorizontalZoom" in html, "applySpectrumHorizontalZoom must be exported to window"
    assert "specChart.options.scales.x.min" in html, "Must set scales.x.min for horizontal zoom"
    assert "specChart.options.scales.x.max" in html, "Must set scales.x.max for horizontal zoom"

    # 3. Wheel & Pan Event Listeners
    assert "chartCanvas.addEventListener('wheel'" in html, "Missing wheel event on chartCanvas"
    assert "chartCanvas.addEventListener('mousedown'" in html, "Missing mousedown pan listener on chartCanvas"
    assert "chartCanvas.addEventListener('dblclick'" in html, "Missing dblclick reset listener on chartCanvas"

    # 4. Array Background and Molecular Markers use dynamic wavelength projection
    assert "getPixelForWl" in html, "spherexArrayPlugin must use getPixelForWl to track sideways zoom"



def test_ice_jump_chips_positioned_below_molecular_signatures():
    """Validates that the 'Ices' quick jump chips are positioned directly below the 'Molecular Signatures' table in the sidebar."""
    html, soup = _get_html_and_soup()

    spectrum_panel = soup.find(id="dockPanelSpectrum")
    assert spectrum_panel is not None, "Missing #dockPanelSpectrum in bottom dock"

    # Find the Molecular Reference Sidebar
    sidebar = spectrum_panel.find(lambda el: el.name == "div" and "Molecular Signatures" in el.get_text())
    assert sidebar is not None, "Missing Molecular Reference Sidebar containing 'Molecular Signatures'"

    # Verify #spec102MolecularBar is located inside the sidebar
    mol_bar = sidebar.find(id="spec102MolecularBar")
    assert mol_bar is not None, "#spec102MolecularBar must be located inside the Molecular Reference Sidebar"

    # Verify the quick jump text and ice pills
    assert "Jump to Ices:" in mol_bar.get_text(), "Missing 'Jump to Ices:' section title in sidebar"
    pills = mol_bar.find_all(class_=lambda c: c and "spec-mol-pill" in c)
    assert len(pills) == 5, f"Expected 5 ice/gas pills, found {len(pills)}"

    # Verify each key molecule/ice is present
    pills_text = " ".join(p.get_text() for p in pills)
    assert "H₂O" in pills_text, "Missing H₂O pill"
    assert "Ice" in pills_text, "Missing Ice pill"
    assert "CH₄" in pills_text, "Missing CH₄ pill"
    assert "CO₂" in pills_text, "Missing CO₂ pill"
    assert "CO" in pills_text, "Missing CO pill"


def test_timestep_relocated_to_left_rail_with_popup_option_contract():
    """Validates that the Time Step controller is relocated to the left vertical toolbar with an interactive popup option."""
    html, soup = _get_html_and_soup()

    # 1. Left tool rail contains #toolTimeStep button
    rail = soup.find(id="leftToolRail")
    assert rail is not None, "Missing #leftToolRail"
    tool_timestep = rail.find(id="toolTimeStep")
    assert tool_timestep is not None, "Missing #toolTimeStep on left tool rail"
    assert "clock" in str(tool_timestep).lower() or "step" in str(tool_timestep).lower()

    # 2. Time Step HUD popup is anchored adjacent to the left rail (left-16)
    hud = soup.find(id="viewportTimeStepHUD")
    assert hud is not None, "Missing #viewportTimeStepHUD"
    classes = hud.get("class", [])
    assert "left-16" in classes, f"#viewportTimeStepHUD must be anchored at left-16, got {classes}"

    # 3. Popup options: Close button and Pinned/Flyout mode button exist
    btn_close = hud.find(id="btnCloseTimeStepHUD")
    assert btn_close is not None, "Missing #btnCloseTimeStepHUD in popup header"
    btn_pin = hud.find(id="btnPinTimeStepHUD")
    assert btn_pin is not None, "Missing #btnPinTimeStepHUD for popup pinning option"

    # 4. Primary functional tools exist inside the popup
    delta_display = hud.find(id="hudTimeStepDelta")
    assert delta_display is not None, "Missing #hudTimeStepDelta"
    btn_prev = hud.find(id="btnHudStepPrev")
    assert btn_prev is not None, "Missing #btnHudStepPrev"
    btn_morph = hud.find(id="btnHudBlinkMorph")
    assert btn_morph is not None, "Missing #btnHudBlinkMorph"
    btn_next = hud.find(id="btnHudStepNext")
    assert btn_next is not None, "Missing #btnHudStepNext"
    btn_diff = hud.find(id="btnHudDiffMode")
    assert btn_diff is not None, "Missing #btnHudDiffMode"
    btn_autoid = hud.find(id="btnAutoDetectPill")
    assert btn_autoid is not None, "Missing #btnAutoDetectPill"

    # 5. Edit Options & Drawer
    btn_edit_opts = hud.find(id="btnTimeStepEditOptions")
    assert btn_edit_opts is not None, "Missing #btnTimeStepEditOptions in HUD header"
    drawer = hud.find(id="timeStepEditDrawer")
    assert drawer is not None, "Missing #timeStepEditDrawer preferences drawer"
    opt_pin = drawer.find(id="optPinAlways")
    opt_unpin = drawer.find(id="optUnpinFlyout")
    assert opt_pin is not None and opt_unpin is not None, "Missing pin and unpin options in edit drawer"
    btn_reset_pos = drawer.find(id="btnResetTimeStepPos")
    assert btn_reset_pos is not None, "Missing #btnResetTimeStepPos in edit drawer"

    # 6. Multiple close options: Header close, Footer close, and Drawer close
    btn_footer_close = hud.find(id="btnTimeStepFooterClose")
    assert btn_footer_close is not None, "Missing #btnTimeStepFooterClose in HUD footer"
    btn_drawer_close = drawer.find(id="btnDrawerCloseTimeStep")
    assert btn_drawer_close is not None, "Missing #btnDrawerCloseTimeStep in edit drawer"

    # 7. Multi-Epoch Scrubbing tools
    blend_slider = hud.find(id="hudEpochBlendSlider")
    assert blend_slider is not None, "Missing #hudEpochBlendSlider"
    chips = hud.find_all(class_=lambda c: c and "hud-epoch-chip" in c)
    assert len(chips) >= 4, f"Expected at least 4 epoch jump chips, found {len(chips)}"

    # 8. JavaScript functions and listeners exported & initialized
    assert "toggleTimeStepHUD" in html, "Missing toggleTimeStepHUD function"
    assert "window.toggleTimeStepHUD" in html, "toggleTimeStepHUD must be exported to window"
    assert "setTimeStepPinned" in html, "Missing setTimeStepPinned function"
    assert "window.setTimeStepPinned" in html, "setTimeStepPinned must be exported to window"
    assert "toggleTimeStepEditDrawer" in html, "Missing toggleTimeStepEditDrawer function"
    assert "initAutoIDAndHUDListeners" in html, "Missing initAutoIDAndHUDListeners function"
    assert "window.initAutoIDAndHUDListeners" in html, "initAutoIDAndHUDListeners must be exported to window"
    assert "toolTimeStep" in html, "JavaScript must bind listener to #toolTimeStep"
    assert "btnCloseTimeStepHUD" in html, "JavaScript must bind listener to #btnCloseTimeStepHUD"
    assert "btnPinTimeStepHUD" in html, "JavaScript must bind listener to #btnPinTimeStepHUD"
    assert "btnTimeStepFooterClose" in html, "JavaScript must bind listener to #btnTimeStepFooterClose"
    assert "btnDrawerCloseTimeStep" in html, "JavaScript must bind listener to #btnDrawerCloseTimeStep"


def test_view_modes_single_tool_icon_and_collective_popup_contract():
    """Validates that Blink, Difference, Spectra, and Aladin Sky tools are consolidated into a single tool icon with a collective popup option."""
    html, soup = _get_html_and_soup()

    # 1. Single tool trigger button in header
    menu_container = soup.find(id="viewModesMenuContainer")
    assert menu_container is not None, "Missing #viewModesMenuContainer"

    trigger_btn = menu_container.find(id="btnViewModesTrigger")
    assert trigger_btn is not None, "Missing #btnViewModesTrigger in header"
    assert trigger_btn.find(id="viewModeActiveLabel") is not None, "Missing #viewModeActiveLabel in trigger button"
    assert trigger_btn.find(id="viewModeChevron") is not None, "Missing #viewModeChevron in trigger button"

    # 2. Collective popup container and all 4 mode options
    popup = menu_container.find(id="viewModesPopup")
    assert popup is not None, "Missing #viewModesPopup container"

    ws_blink = popup.find(id="wsBlink")
    assert ws_blink is not None, "Missing #wsBlink inside collective viewModesPopup"
    assert "B" in ws_blink.get_text(), "Missing hotkey B badge on #wsBlink"

    ws_diff = popup.find(id="wsDiff")
    assert ws_diff is not None, "Missing #wsDiff inside collective viewModesPopup"
    assert "D" in ws_diff.get_text(), "Missing hotkey D badge on #wsDiff"

    ws_spec = popup.find(id="wsSpec")
    assert ws_spec is not None, "Missing #wsSpec inside collective viewModesPopup"
    assert "S" in ws_spec.get_text(), "Missing hotkey S badge on #wsSpec"

    ws_aladin = popup.find(id="wsAladin")
    assert ws_aladin is not None, "Missing #wsAladin inside collective viewModesPopup"
    assert "A" in ws_aladin.get_text(), "Missing hotkey A badge on #wsAladin"

    # 3. JavaScript functions and event wiring
    assert "toggleViewModesPopup" in html, "Missing toggleViewModesPopup JavaScript function"
    assert "closeViewModesPopup" in html, "Missing closeViewModesPopup JavaScript function"
    assert "updateActiveViewModeIndicator" in html, "Missing updateActiveViewModeIndicator JavaScript function"
    assert "window.toggleViewModesPopup" in html, "toggleViewModesPopup must be exported to window"
    assert "btnViewModesTrigger" in html, "btnViewModesTrigger must have event listeners bound"









