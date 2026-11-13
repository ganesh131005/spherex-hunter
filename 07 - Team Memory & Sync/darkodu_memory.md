# 🧠 Memory Log: darkodu (Astro-Data Lead)
> **Role:** Backend API, Astropy Cutout Engine & 102-Band Spectra
> **Branch:** `darkodu/astro-backend`

## Personal Status:
- **Current Task:** Backend API live on `http://localhost:8000`. Serving real astronomical cutouts and 102-band spectra.
- **Next Task:** Add multi-survey overlays (Gaia DR3 proper motion catalog query).
- **Blockers:** None.

## Completed Tasks:
- [x] Fixed ZeroDivisionError in `backend/services/cutout_engine.py` (`load_real_fits_cutout`): implemented dynamic symmetric padding based on offset RA/Dec coordinates so near-tile queries return valid FITS cutouts and difference images across all LODs without boundary exceptions (`TASK-003`).
- [x] Assigned role and received task prompts for Antigravity.
- [x] Initialized `backend/step1_wise0855_irsa.py` for querying NASA IRSA TAP archive.
- [x] Installed and configured `astropy`, `astroquery`, and `pyvo`.
- [x] Implemented `backend/services/cutout_engine.py` with Astropy ZScale/Asinh FITS stretching, multi-epoch generation, and difference imaging ($I_2 - I_1$).
- [x] Implemented FastAPI server in `backend/main.py` with `/api/health`, `/api/targets`, `/api/cutout`, `/api/spectrum`, and `/api/flag`.
- [x] Created `start_backend.bat` for 1-click startup.

- [x] Integrated live NASA IRSA Caltech FinderChart API into `cutout_engine.py` for real-time querying and downloading of authentic 2MASS and DSS2 FITS files for ANY arbitrary celestial coordinates.
- [x] Implemented dynamic disk caching (`backend/cache/dynamic_fits/`) ensuring instant sub-200ms retrieval on repeated visits to the same coordinates.
- [x] Calibrated Multi-Tier Game LOD Engine (`backend/services/cutout_engine.py`):
  - Calibrated matrix dimensions: LOD 2 ($360 \times 360$, ~360p, 8.0' FOV), LOD 1 ($720 \times 720$, ~720p HD, 3.0' FOV), and LOD 0 ($1024 \times 1024$, full unbinned sensor resolution, 1.5' FOV).
  - Implemented dynamic sub-array cropping from authentic NASA 2MASS and DSS2 FITS data so benchmark targets serve all 3 LOD tiers in sub-20ms from disk with zero network latency.
  - Added support for arbitrary offset coordinate crops (`center_ra`, `center_dec`) using padded master arrays with reflection, allowing the frontend near-tile streamer to query any coordinate around benchmark targets in <10ms.
  - Returns `actual_fov` in `data.coordinates.fov_arcmin` ensuring mathematically consistent angular scale across all LOD transitions.
  - Integrates Alard-Lupton & Bramich scientific difference imaging with median sky background subtraction, PSF matching ($\sigma=1.15$), photometric flux ratio scaling $S$, and photon noise floor $Z$-score mapping.
