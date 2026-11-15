# 📊 SPHEREx Hunter Viewport Overhaul: Baseline Status & Audit Report (Step 0)

> **Document:** `docs/viewport_status.md`  
> **Repository:** `joker0210G/spherex-hunter` | **Branch:** `darkodu/astro-backend`  
> **Authors:** `darkodu` (Astro-Data) & `coolodu` (Frontend/Blink UI)  
> **Audit Date:** 2026-11-15 | **Release Baseline:** NASA SPHEREx DR1 (Pipeline v2.1.0)

---

## 1. Branch Sync & Diff Analysis

A full fetch and diff inspection against the remote repository was performed:
- **Command:** `git fetch origin coolodu/web-frontend; git diff --stat HEAD..origin/coolodu/web-frontend`
- **Result:**
  ```text
   07 - Team Memory & Sync/SHARED_PROJECT_STATE.md | 5 -----
   07 - Team Memory & Sync/jokerodu_memory.md      | 4 ----
   2 files changed, 9 deletions(-)
  ```
- **Finding:** The working branch `darkodu/astro-backend` is fully integrated with all frontend redesign work from `origin/coolodu/web-frontend` (`1d86f8a`) and `origin/main` (`eb8b3c8`). There are zero code divergence conflicts in `frontend/index.html` or `backend/`.

---

## 2. Security, Hardcoding & Licensing Audit

1. **Exposed Secrets & Filesystem Paths:**
   - Automated regex scanning found **0 absolute filesystem paths** (e.g. `C:\...`) and **0 exposed API keys or secrets** in `frontend/index.html` or backend routes.
2. **Hardcoded Scientific Metadata:**
   - Scanned for hardcoded observation dates (`DATE-OBS`), Modified Julian Dates (`MJD-OBS`), and synthetic Bayesian detection probabilities.
   - A single static string was identified in `frontend/index.html:1639` inside the educational modal copy (*"Validated on authentic NASA SPHEREx flight exposures (MJD 60789.752254, Detector 6)"*), citing the published validation benchmark.
   - All dynamic UI displays (`#vpFrameLabel`, `#hudTimeStepDelta`, `#inspectorPanelTarget`) strictly pull from backend JSON endpoints and FITS header payloads (`data.epochs[]`, `data.difference_image`).
3. **Open-Source Licensing:**
   - Dependencies adhere to MIT / Apache 2.0 / BSD 3-Clause licenses (Astropy, FastAPI, Aladin Lite v3, Lucide).

---

## 3. NASA SPHEREx DR1 / QR3 Pipeline & `demo_cache` Audit

### A. Cached JSON Manifests (`demo_cache/`)
Audit of `demo_cache/*/difference.json`, `exposures.json`, and `candidates.json`:
- **`data_release`:** `DR1` across all targets (`wise0855`, `barnard`, `epsindi`, `rwaur`, `rdraconis`, `sample_leo`).
- **`pipeline_version`:** `2.1.0` uniformly recorded across all manifests.
- **Verification:** All precomputed targets derive from the uniformly reprocessed DR1 pipeline, guaranteeing consistency with NASA SPHEREx Data Release 1.

### B. Calibrated FITS Level 2 Exposure Products (`data_samples/`)
Direct FITS header extraction on calibrated level 2 products:
- `data_samples/spherex_level2_sample.fits` (HDU 1 `IMAGE`):
  - `EXPIDN = 202517402000111`
  - `DATE-OBS = 2025-04-24T18:01:05.843`
  - `MJD-OBS = 60789.750762072`
  - `TELAPSE = 118.1873 s`
- `data_samples/spherex_level2_pair_epoch2.fits` (HDU 1 `IMAGE`):
  - `EXPIDN = 202517402000121`
  - `DATE-OBS = 2025-04-24T18:03:14.774`
  - `MJD-OBS = 60789.752254329`
  - `TELAPSE = 118.1873 s`
- `data_samples/wise0855_spherex_d6.fits` (HDU 1 `IMAGE`):
  - `DATE-OBS = 2025-11-10T23:29:00.994`
  - `MJD-OBS = 60989.978483727`

### C. IRSA ObsCore Database Records (`data_samples/irsa_obscore_dr1_cache.json`)
- All 6 target fields contain authentic IRSA ObsCore records with:
  - `obs_collection = 'spherex_dr1'`
  - `data_release = 'DR1'`
  - Exact IVOA spatial footprints (`s_region = POLYGON ICRS ...`)
  - Authentic exposure counts: WISE 0855 (258), Barnard's Star (363), Epsilon Indi B (459), RW Aurigae (374), R Draconis (2542), Leo Minor (262).

### D. Single-Cube vs. Per-Survey HiPS Determination (Amendment A9)
Inspection of IRSA's official SPHEREx HiPS properties (`https://irsa.ipac.caltech.edu/data/hips/SPHEREx/spherex_allsky_cube/properties`):
- `obs_title = SPHEREx DR1 all-sky data cube`
- `t_min = 60789.75076` (April 2025)
- `t_max = 61174.49276` (May 2026)
- `dataproduct_type = cube` (102 frames, 1 per channel across Bands 1–6)
- **Conclusion:** **IRSA provides a SINGLE MERGED/CO-ADDED all-sky data cube** spanning the full DR1 mission timeline, **NOT separate per-survey cubes**.
- **Scientific Implication:** High-proper-motion objects (e.g. WISE 0855 at $8.15''/\text{yr}$) shift by over $1.3$ native SPHEREx pixels during this interval and are **blurred/smeared in the HiPS mosaic**. Moving object identification and blink differencing MUST rely on individual calibrated exposures (`/api/v1/exposures`), not the HiPS mosaic.

---

## 4. The 7 Core Requirements: Status & Gap Analysis

| # | Core User Requirement | Current Code Reference | Status | Architectural Gap & Required Action |
| :-: | :--- | :--- | :-: | :--- |
| **1** | **Authentic NASA SPHEREx Metadata & Imagery** | `backend/services/scene_service.py:32`, `frontend/index.html:597` | **Partial** | 102 channels displayed, but requires deterministic generation script (`scripts/generate_spherex_channels.py`) from IRSA metadata; persistent `NASA/JPL-Caltech/IPAC` attribution badge required in viewport HUD. |
| **2** | **Interactive Logarithmic Zoom Bar** | `frontend/index.html:577`, `frontend/index.html:5349` | **Missing** | Viewport currently uses discrete buttons (`🌌 180°`, `✨ 30°`, etc.) and mouse wheel. Requires vertical Google Maps-style zoom bar with logarithmic slider, ARIA `role="slider"`, cursor-centered zoom, and dual scale markers (**HiPS Native** vs. **Exposure Native $6.15''/\text{px}$**). |
| **3** | **Scoped Multi-Tier Caching System** | `frontend/index.html:3286`, `backend/services/cutout_engine.py:80` | **Partial** | L0 RAM LRU (`adjacentSkyTileCache`) and L1 IndexedDB exist, but require strict scoping separation (Aladin handles HiPS; custom cache strictly handles exposure cutouts/differences), integer quantized micro-degree keys, and cross-browser idle prefetch fallbacks. |
| **4** | **Uniform Resolution & LOD at Max Zoom-Out** | `frontend/index.html:3360` | **Partial** | HiPS at wide view uses uniform order, but canvas spatial tile mosaic requires strict uniform LOD order enforcement without multi-scale divergence. |
| **5** | **Seamless Single-Tile Appearance at Zoom-Out** | `frontend/index.html:3374` | **Partial** | Sub-pixel overlap added, but requires elimination of wireframes and complete topological continuity. |
| **6** | **Progressive Detail on Zoom-In** | `frontend/index.html:3810` | **Partial** | LOD 2 $\to$ LOD 1 $\to$ LOD 0 exists, but clean handoff to calibrated exposures at $10'\text{--}30'$ science FOV with nearest-neighbor `"Show Native Pixels"` toggle is required. |
| **7** | **Accurate Multi-Epoch Placement** | `backend/services/cutout_engine.py`, `frontend/index.html:528` | **Partial** | Multi-epoch HUD exists, but WISE 0855 requires multi-exposure narrowband stack around $4.6\,\mu\text{m}$ (matching W2), and backend Gaia DR3 registration requires `apply_space_motion` + EPSF centroid residual reporting. |

---

## 5. Baseline Test Execution Results

- **Command:** `.venv\Scripts\python.exe -m pytest tests/test_golden_suite.py tests/test_api_v1_contract.py tests/test_ui_contract.py`
- **Output:** **49 passed, 0 failed** in 9.37s.
- **Contract Integrity:** Core API v1 contracts and UI headless DOM assertions pass 100% green before any code modifications.
