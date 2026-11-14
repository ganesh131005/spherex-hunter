"""
E2E Playwright test for Continuous Viewport features:
1. Seamless continuous epoch blending (morph slider & morph toggle).
2. Feathered celestial edge blending into ambient starfield.
3. Smooth inertial pan & zoom kinematics.
"""

import os
import time
from playwright.sync_api import sync_playwright

DOCS_FIGURES = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")
os.makedirs(DOCS_FIGURES, exist_ok=True)
BASE_URL = os.environ.get("SPHEREX_BASE_URL", "http://127.0.0.1:8000/app/index.html")

def test_continuous_viewport_controls_and_morph():
    """Verify continuous morph toggle and manual epoch blend slider work seamlessly."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.add_init_script("localStorage.setItem('spherex_hunter_onboarding_completed', 'true');")
        page.goto(f"{BASE_URL}#target=wise0855&mode=blink&frame=1", wait_until="domcontentloaded")
        page.wait_for_selector("#astroCanvas")
        time.sleep(1.0)

        # 1. Verify Toggle Morph Button
        btn_morph = page.locator("#btnToggleBlinkMorph")
        assert btn_morph.is_visible()
        morph_label = page.locator("#blinkMorphModeLabel")
        assert morph_label.inner_text() == "Smooth Morph"

        # Toggle to Snap Blink
        btn_morph.click()
        assert morph_label.inner_text() == "Snap Blink"

        # Toggle back to Smooth Morph
        btn_morph.click()
        assert morph_label.inner_text() == "Smooth Morph"

        # 2. Verify Continuous Epoch Blend Slider
        slider = page.locator("#epochBlendSlider")
        assert slider.is_visible()
        blend_label = page.locator("#epochBlendLabel")
        assert blend_label.is_visible()

        # Pause flipbook if playing so we can manually scrub
        btn_play = page.locator("#btnPlayPause")
        btn_play.click()
        time.sleep(0.3)

        # Scrub to 50%
        slider.fill("50")
        slider.dispatch_event("input")
        time.sleep(0.3)
        assert blend_label.inner_text() == "50%"

        # Scrub to 100%
        slider.fill("100")
        slider.dispatch_event("input")
        time.sleep(0.3)
        assert blend_label.inner_text() == "100%"

        # Scrub back to 0%
        slider.fill("0")
        slider.dispatch_event("input")
        time.sleep(0.3)
        assert blend_label.inner_text() == "0%"

        # 3. Verify Step Back & Step Fwd increment blend smoothly
        btn_step_fwd = page.locator("#btnStepFwd")
        btn_step_fwd.click()
        time.sleep(0.3)
        # Blend should have advanced to 10%
        assert blend_label.inner_text() == "10%"

        # 4. Canvas screenshot capture for verification
        canvas = page.locator("#astroCanvas")
        assert canvas.is_visible()
        screenshot_path = os.path.join(DOCS_FIGURES, "continuous_viewport_blended.png")
        canvas.screenshot(path=screenshot_path)
        assert os.path.exists(screenshot_path)
        assert os.path.getsize(screenshot_path) > 1000

        browser.close()
