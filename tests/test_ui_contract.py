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
import re
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
