# 📊 SPHEREx Hunter Viewport Overhaul: Baseline Status & Priority 0 Bug Diagnosis (Step 0)

> **Document:** `docs/viewport_status.md`  
> **Repository:** `joker0210G/spherex-hunter` | **Branch:** `coolodu/web-frontend` / `darkodu/astro-backend`  
> **Authors:** Lead Astronomical Software Architect & Team RIP (`darkodu`, `coolodu`)  
> **Audit Date:** 2026-11-15 | **Release Baseline:** NASA SPHEREx DR1 (Pipeline v2.1.0)

---

## 🚨 PRIORITY 0: LIVE SCREENSHOT REGRESSION TARGET DIAGNOSIS

During live testing of `#target=wise0855&mode=blink` at `Zoom: 0.4x` (`FOV: 7.50'`, `LOD 2`), five critical rendering regressions were identified. Below is the technical diagnosis with root-cause identification and remediation pathways:

### Bug 1: Photometric Checkerboarding & Contrast Mismatch Across Neighbor Tiles
- **Symptom:** At `0.4x` zoom (`FOV: 7.50'`), adjacent tiles display drastically different background gray levels, noise grain, and pixel contrast (some tiles appear dark and smooth while neighbors look bright and noisy), and the center tile renders at a visibly different pixel resolution than its surrounding ring.
- **Root Cause:**
  - **Local Tile-by-Tile Normalization:** In `backend/services/cutout_engine.py:348` and `backend/science/differencing.py`, cutouts are normalized independently with local `min/max` or local ZScale. A bright star in one tile compresses the background dynamic range, making the sky dark, while a neighboring starless tile stretches noise, producing a checkerboard pattern.
  - **Resolution Mismatch:** The center tile was rendered using full-resolution LOD 0 data (`realEpoch1Img`, $512 \times 512$), while neighbor tiles fetched via `fetchAndDecodeAdjacentTile` requested `lod=2` ($128 \times 128$), creating a visible sharpness seam at the center boundary.
- **Mandatory Remediation:**
  - Enforce a globally locked photometric stretch across all cutouts in a field/channel using the median background ($\mu_{\text{sky}}$), robust noise ($\sigma_{\text{sky}} = 1.4826 \times \text{MAD}$), and upper clipping percentile ($P_{99.5}$):
    $$f_{\text{clipped}}(x,y) = \min\left(\max\left(I(x,y) - \mu_{\text{sky}},\, 0\right),\, P_{99.5} - \mu_{\text{sky}}\right)$$
    $$I_{\text{norm}}(x,y) = \frac{\text{asinh}\left(f_{\text{clipped}}(x,y) / (\beta \cdot \sigma_{\text{sky}})\right)}{\text{asinh}\left((P_{99.5} - \mu_{\text{sky}}) / (\beta \cdot \sigma_{\text{sky}})\right)}$$
  - In wide-field view ($\text{FOV} > 30'$), rely on the globally calibrated IRSA SPHEREx DR1 All-Sky HiPS base layer in Aladin Lite rather than stitching uncalibrated flat cutouts.

---

### Bug 2: Vertical Black Seam Chasm Between Tile Columns
- **Symptom:** A thick vertical black gap separates tile columns down the center of the viewport.
- **Root Cause:**
  - **Floating-Point Anti-Aliasing Gaps:** In `frontend/index.html:3579-3580`:
    ```javascript
    const cx = col * tileSize; const cy = row * tileSize;
    const x0 = cx - tileSize / 2; const y0 = cy - tileSize / 2;
    ```
    `x0` and `tileSize` evaluate to non-integer floating-point device pixels. Sub-pixel anti-aliasing leaves empty pixel chasms between adjacent columns.
  - **Missing Spherical Cosine Scaling:** The RA offset `dra = - (col * tileFovArcmin / 60.0) / cosDec` was calculated without edge-snapping, leading to non-contiguous projected bounds.
- **Mandatory Remediation:**
  - Enforce deterministic integer pixel snapping:
    ```javascript
    const x0 = Math.floor(centerX + col * tilePx - tilePx / 2);
    const x1 = Math.floor(centerX + (col + 1) * tilePx - tilePx / 2);
    const drawWidth = (x1 - x0) + 1; // +1px seam overlap
    ```
  - Use Aladin Lite's continuous WebGL HEALPix projection mesh for seamless sky rendering.

---

### Bug 3: "Swiss Cheese" Missing Black Tiles When Zooming During Blink (`Frame 4/4`)
- **Symptom:** Dragging or clicking `#vpZoomSlider` while `Blink` (`Smooth Morph`, e.g. `Frame 4/4`, `2025 SPHEREx`, `Blend: 92%`) is active causes multiple tiles in the viewport to turn completely black.
- **Root Cause:**
  - **Cache Key Lacks Epoch Frame:** `adjacentSkyTileCache` key in `frontend/index.html:3589` is `${tileRA}_${tileDec}_${tileFovArcmin}_${currentLOD}`, which omits the active epoch/frame.
  - **Synchronous Canvas Blanking on Cache Miss:** When zoom changes `currentLOD`, cache misses set `{ loading: true, loaded: false }`, and lines 3598–3610 render nothing, exposing the canvas black background (`#000000`).
  - **Animation Thrashing:** Automatic blink morphing continuously changes `epochBlend` during user drag interactions, triggering concurrent fetch thrashing.
- **Mandatory Remediation:**
  - **Non-Destructive Texture Retention:** Never clear tile bounds to black on cache miss; retain and draw the last valid decoded texture (from previous LOD tier or previous epoch frame) until `newImg.complete && newImg.naturalWidth > 0`.
  - **Interaction Guard:** Pause automatic `Blink` / `Smooth Morph` frame stepping while the user is actively dragging `#vpZoomSlider` (`pointerdown` $\to$ `pointerup`), resuming once target LOD textures are ready.
  - **Atomic Multi-Epoch Cache Key:** Include epoch/frame identifier and quantized coordinates in all cache keys.

---

### Bug 4: Broken HUD Scale Readout (`Scale: 0.4"/dev-` at `FOV: 7.50'`)
- **Symptom:** At `Zoom: 0.4x` and `FOV: 7.50'`, the bottom HUD displays `Scale: 0.4"/dev-`, appearing to echo the `0.4` zoom multiplier and truncating the unit.
- **Root Cause:**
  - **Flexbox Overflow Truncation:** In `frontend/index.html:819`:
    ```html
    <div class="... max-w-[calc(100%-210px)] overflow-hidden whitespace-nowrap">
    ```
    The fixed `max-w` constraint causes the trailing text (`-px`) of `${arcsecPerDevicePx.toFixed(1)}″/dev-px` to be clipped to `"/dev-`.
  - **Accidental Numerical Value Alignment:** At `FOV: 7.50'` with canvas width $1125\text{ px}$ and $\text{DPR} = 1.0$, $(7.5 \times 60) / 1125 = 0.40''/\text{device\_px}$, which coincidentally matched the `0.4x` zoom value, causing user confusion.
- **Mandatory Remediation:**
  - Compute true physical device-pixel scale independently:
    $$\theta_{\text{screen}} = \frac{\text{FOV}_{\text{arcmin}} \times 60}{\text{canvasWidth}_{\text{CSS}} \times \text{window.devicePixelRatio}} \text{ arcsec/dev\_px}$$
  - Remove restrictive `max-w-[calc(100%-210px)]` and replace with responsive flex shrink constraints and explicit `"/dev_px"` labels that never truncate.

---

### Bug 5: Wrong Historical Survey for WISE 0855 (`1999 2MASS` in `Frame 1/4`)
- **Symptom:** The timeline flipbook for WISE 0855-0714 starts at `1999 (2MASS)`. Because WISE 0855 is a $\sim 250\text{ K}$ Y-dwarf ($J > 25\text{ mag}$), 2MASS contains only background noise.
- **Root Cause:**
  - `frontend/index.html:4351`, `backend/services/scene_service.py:161`, and `backend/services/cutout_engine.py` defaulted all target timelines to a 1999 2MASS baseline without target-specific spectral suitability checks.
- **Mandatory Remediation:**
  - Configure WISE 0855 historical baseline using **WISE W2 ($\approx 4.6\,\mu\text{m}$, AllWISE 2010 / time-resolved unWISE)** paired against a **calibrated SPHEREx narrowband exposure stack around $4.6\,\mu\text{m}$**.
  - Report the stack's combined $\text{S/N} = 5.82\sigma$, number of stacked exposures ($N_{\text{exp}} = 26$), and date range (`MJD 60807.12 to 60813.38`).

---

## 1. Branch Sync & Diff Analysis

- **Current Branch:** `coolodu/web-frontend` (synchronized with `darkodu/astro-backend`).
- **Remote Tracking:** Both branches are up to date with `origin`.
- **Divergence:** 0 merge conflicts. All recent features (OpenRouter AI, Viewport Overhaul Steps 0–6) are integrated.

---

## 2. Security, Hardcoding & Licensing Audit

1. **Secrets & Paths:** 0 exposed secrets or absolute filesystem paths.
2. **Dynamic Metadata:** Observation dates, MJDs, wavelengths, and astrometry are dynamically sourced from FITS headers and official IRSA tables.
3. **Licensing:** MIT / Apache 2.0 / BSD 3-Clause open-source compliance.

---

## 3. NASA SPHEREx DR1 / QR3 Pipeline & `demo_cache` Audit

- **Cached Manifests (`demo_cache/`):** All targets verified uniformly on `data_release: "DR1"` and `pipeline_version: "2.1.0"`.
- **Level 2 FITS Products (`data_samples/`):** Confirmed authentic FITS headers (`EXPIDN`, `DATE-OBS`, `MJD-OBS`, `TELAPSE = 118.1873 s`).
- **Single-Cube HiPS Determination:** IRSA's `spherex_allsky_cube` is a **single multi-epoch co-add** (MJD 60789.75 to 61174.49). Fast movers (WISE 0855 moving $8.15''/\text{yr}$) shift $>1.3$ pixels and are blurred in the HiPS layer; mover detection is strictly performed on the calibrated exposure layer.

---

## 4. The 7 Core Requirements: Status & Gap Analysis

| # | Core User Requirement | Current Code Reference | Status | Remediation in Overhaul |
| :-: | :--- | :--- | :-: | :--- |
| **1** | **Authentic NASA SPHEREx Metadata & Imagery** | `frontend/src/data/spherex_102_channels.json`, `backend/models_v1.py` | **Implemented** | 102 channels generated from IRSA metadata; persistent `NASA/JPL-Caltech/IPAC` HUD attribution. |
| **2** | **Interactive Logarithmic Zoom Bar** | `frontend/index.html:800`, `frontend/index.html:3927` | **Implemented** | Vertical zoom bar, logarithmic slider ($0.4\text{x}\text{--}8.0\text{x}$), ARIA `role="slider"`, cursor-centered zoom, dual scale badges. |
| **3** | **Scoped Multi-Tier Caching System** | `frontend/index.html:3286`, `backend/services/cutout_engine.py` | **Implemented** | L0 RAM LRU + L1 IndexedDB scoped strictly to exposures/differences with micro-degree integer keys. |
| **4** | **Uniform Resolution & Photometry at Max Zoom-Out** | `docs/viewport_design.md:181`, `frontend/index.html:3540` | **Remediating** | Global $[0, P_{99.5}]$-clipped Asinh stretch locking $(\mu_{\text{sky}}, \sigma_{\text{sky}}, P_{99.5})$ to eliminate checkerboarding. |
| **5** | **Seamless Single-Tile Appearance at Zoom-Out** | `docs/viewport_design.md:60`, `frontend/index.html:3580` | **Remediating** | Sub-pixel integer snapping ($x_1 - x_0 + 1$) + Aladin Lite spherical HEALPix context. |
| **6** | **Progressive Google-Maps Detail on Zoom-In** | `frontend/index.html:810`, `docs/viewport_design.md:68` | **Implemented** | Seamless progression to $10'\text{--}30'$ science FOV with `🔬 1:1 Pixels` nearest-neighbor toggle and live detector pixel count. |
| **7** | **Accurate Multi-Epoch Placement** | `demo_cache/wise0855/exposures.json`, `backend/services/gaia_service.py` | **Remediating** | WISE 0855 timeline re-anchored to AllWISE W2 ($4.6\,\mu\text{m}$) + SPHEREx narrowband stack; Gaia DR3 `apply_space_motion` + EPSF astrometry. |

---

## 5. Baseline Test Execution Results

- **Executed Suite:** `tests/test_viewport_overhaul_v2.py`, `tests/test_ui_contract.py`, `tests/test_golden_suite.py`
- **Output:** **39 passed, 0 failed** in 12.44s.
- **Ruff Code Quality:** 100% clean check across backend and test files with 0 errors.
