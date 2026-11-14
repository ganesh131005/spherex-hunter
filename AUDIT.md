# 🔍 SPHEREx Hunter - Right Sidebar & Layer Architecture Audit

**Date:** 2026-11-14  
**Auditor:** Team RIP (Antigravity AI Co-Pilot)  
**Target Component:** Right Sidebar (`#propertiesSidebar`, "Scene Collection", Outliner & Telemetry Panel)

---

## 1. Executive Summary & Root Cause Analysis

Upon inspecting `frontend/index.html`, `backend/services/cutout_engine.py`, `backend/services/catalog_engine.py`, and reproducing the live application behavior in Playwright headless Chromium, we identified **7 core architectural and scientific failures** in the existing implementation:

### 🚨 Root Cause 1: Hardcoded Outliner Tree (No State-Driven Renderer)
* **Location:** `frontend/index.html` lines 331–365
* **Issue:** The "Scene Collection" tree was hardcoded with static HTML DOM nodes:
  - `Observatory Collection`
  - `SPHEREx Telescope (Active)`
  - `WISE 0855-0714 (Y-Dwarf)`
  - `Epoch 1 (2MASS 1.25μm) (1999-02)`
  - `Epoch 2 (SPHEREx Co-add) (2025-05)`
* **Impact:** Regardless of which target was clicked (Barnard's Star, RW Aurigae, custom coordinates), the epoch rows and telescope status remained permanently static. There was no reactive state object (`scene`), no layer hierarchy, and no dynamic rendering.

### 🚨 Root Cause 2: Unit Discrepancy & Absurd Astronomical Figures
* **Location:** `frontend/index.html` line 1585 & `backend/services/cutout_engine.py` line 585
* **Issue:** The backend returned proper motion in milliarcseconds per year (`proper_motion_mas_yr = 14160.00` or `8550.00`), but the frontend formatted it with arcseconds per year:
  ```javascript
  document.getElementById('propPM').innerText = `${data.telemetry.proper_motion_mas_yr.toFixed(2)} "/yr`;
  ```
* **Impact:** The UI displayed `Proper Motion (μ): 14160.00 "/yr` for WISE 0855 and `10393.40 "/yr` for Barnard's Star! In reality, Barnard's Star is $\approx 10.39''/\mathrm{yr}$ ($10393.4\,\mathrm{mas/yr}$) and WISE 0855 is $\approx 8.12\text{--}8.55''/\mathrm{yr}$ ($8550\,\mathrm{mas/yr}$). Showing 14,000 arcseconds per year is off by a factor of 1,000!

### 🚨 Root Cause 3: Inverted Temperature Precedence Bug in Backend
* **Location:** `backend/services/cutout_engine.py` lines 440–455
* **Issue:** The function `extract_spectrum_and_telemetry()` checked `if d1 is not None and d2 is not None` *before* checking `elif target_key in BENCHMARKS`.
* **Impact:** Because normalized FITS array slices were always present, `ratio = f_nir / f_opt` evaluated to $\approx 1.0$. The function fell into the fallback branch `else: temp = 5200` (Warm stellar source). Consequently, **WISE 0855-0714** (an ultracold Y-dwarf at $T_{\mathrm{eff}} \approx 250\,\mathrm{K}$) was falsely reported to the user as `~5200 K` (the temperature of a G-type star like the Sun!).

### 🚨 Root Cause 4: Scientifically Contradictory "Planet X 98%" & NEOSSat Card
* **Location:** `frontend/index.html` lines 437–468 & `backend/services/csa_neossat_service.py`
* **Issue:** The sidebar displayed a hardcoded card claiming:
  - `Tracked Object: 2014 QX39`
  - `Diurnal Rate: 28.4 "/hr`
  - `Planet X Prob: 98% (Sub-stellar)`
* **Impact:** A diurnal motion rate of $28.4''/\mathrm{hr}$ is characteristic of an inner-solar-system asteroid or Near-Earth Object (NEO). A hypothetical outer Planet X at $\ge 300\,\mathrm{AU}$ would move at $\ll 0.1''/\mathrm{yr}$ (or $\approx 0.00001''/\mathrm{hr}$). Stating both $28.4''/\mathrm{hr}$ and "Planet X Prob 98%" on the same object is scientifically contradictory and unscientific.

### 🚨 Root Cause 5: Missing Proper-Motion Coordinate Propagation
* **Location:** `backend/services/cutout_service.py` & `frontend/index.html`
* **Issue:** Cutouts for Epoch 1 (2MASS 1999) and Epoch 2 (SPHEREx 2025) were requested at the exact same fixed coordinates $(\alpha_0, \delta_0)$ without applying proper-motion space motion:
  $$\Delta t = 2025.5 - 1999.2 = 26.3\,\text{years}$$
  For Barnard's Star ($\mu \approx 10.4''/\mathrm{yr}$), displacement $\Delta \theta \approx 273'' \approx 4.55'$. In a $3'$ FOV, Barnard's Star in 1999 was outside the 2025 field!
* **Impact:** Blinking between epochs without proper motion propagation either showed an empty field in one epoch or caused severe misalignment.

### 🚨 Root Cause 6: No Interactive Layer Controls or Canvas Synchronization
* **Location:** `frontend/index.html` (Blink viewer and Aladin Lite canvas)
* **Issue:** The layers (Base Epoch Image, Difference Map, Gaia Vector Overlay, Candidate Markers) had no unified state, no opacity sliders, no visibility toggles in the right sidebar, and no ability to define Blink Frame A and Frame B interactively.
* **Impact:** The "Scene Collection" panel was purely cosmetic and could not be used as an actual layer manager.

### 🚨 Root Cause 7: Zero/Black Padding Instead of Transparent Alpha Mask
* **Location:** `backend/services/cutout_engine.py`
* **Issue:** Edge pixels outside survey coverage were filled with zero values ($0.0$).
* **Impact:** Stretched to 8-bit images, missing coverage appeared as pitch black rectangles instead of transparent pixels with a designated coverage mask.

---

## 2. Remediation Strategy & Action Plan

1. **Backend Schema & Telemetry Validation (`backend/services/catalog_engine.py`):**
   - Introduce Pydantic schema validation for all target metadata (`AstronomicalTargetMetadata`).
   - Physical plausibility checks: reject $T_{\mathrm{eff}} > 600\,\mathrm{K}$ for Y-dwarfs; flag $\mu > 20''/\mathrm{yr}$ unless verified (Barnard's star is $10.4''/\mathrm{yr}$).
   - Cite authoritative literature sources (Gaia DR3, SIMBAD, Kirkpatrick et al., Luhman 2014).
   - Fix temperature precedence so verified benchmark temperatures are never overwritten by noisy image ratios.

2. **Astropy Proper-Motion Epoch Propagation (`backend/services/motion_service.py`):**
   - Use `astropy.coordinates.SkyCoord.apply_space_motion()` to propagate coordinates from $t_0$ to any epoch's observation date (MJD / Besselian epoch).
   - Provide dual centers (epoch center vs baseline center) and trigger displacement warnings if $\Delta \theta > \text{FOV}$.

3. **Transparent NaN & Coverage Masking (`backend/services/cutout_engine.py`):**
   - Retain `NaN` values for unobserved pixels; generate RGBA PNGs with alpha = 0 for `NaN` pixels.
   - Return explicit coverage mask statistics and support "Show Coverage Mask" layer.

4. **Evidence Tier Classification (Replacing Planet X 98%):**
   - Tier 1: Known Solar System Object (asteroid/comet confirmed by MPC/NEOSSat, diurnal motion $> 1''/\mathrm{hr}$).
   - Tier 2: Known Star or Brown Dwarf (confirmed by Gaia DR3 / SIMBAD, high proper motion $\mu > 100\,\mathrm{mas/yr}$).
   - Tier 3: Unknown Mover (unmatched in Gaia DR3, dipole visible in difference image, not confirmed).
   - Tier 4: Slow IR-Excess Candidate (persistent infrared flux $W1-W2 > 1.5$, $\mu < 0.1''/\mathrm{yr}$, uncatalogued, not confirmed).

5. **Single Source of Truth `scene` State Engine (`frontend/index.html`):**
   - Define reactive `window.scene` object:
     ```javascript
     scene = {
       target: { name, ra, dec, pm_ra, pm_dec, plx, dist_pc, teff_k, spectral_type, evidence_tier, citations },
       epochs: [
         { id, survey, instrument, band, wavelength_um, mjd, obs_date, product_id, pixel_scale, units, status, cutout_center, fov_arcmin }
       ],
       layers: [
         { id: 'base_epoch_a', name: 'Epoch A Base Image', visible: true, opacity: 1.0, type: 'raster' },
         { id: 'base_epoch_b', name: 'Epoch B Base Image', visible: true, opacity: 1.0, type: 'raster' },
         { id: 'diff_image', name: 'Difference Image (B - A)', visible: false, opacity: 1.0, type: 'diff', valid_bands: true },
         { id: 'coverage_mask', name: 'Coverage Mask (NaN)', visible: false, opacity: 0.5, type: 'mask' },
         { id: 'gaia_overlay', name: 'Gaia DR3 Astrometry Vectors', visible: true, opacity: 0.85, type: 'vector' },
         { id: 'candidate_markers', name: 'Citizen Science Markers', visible: true, opacity: 1.0, type: 'overlay' }
       ]
     }
     ```
   - Render entire sidebar dynamically from `scene` with ARIA roles, collapsible accordions, keyboard accessibility, opacity sliders, and A/B frame assigners.
   - Synchronize layer toggles and sliders directly with the HTML5 Canvas blink loop and Aladin Lite.

6. **Automated Verification:**
   - Playwright end-to-end tests verifying layer toggling, opacity updates, preset switching, and absence of hardcoded values.
   - Pytest unit tests for Astropy space motion propagation and metadata validation.
