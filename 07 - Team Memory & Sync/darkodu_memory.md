# 🧠 Memory Log: darkodu (Astro-Data Lead)
> **Role:** Backend API, Astropy Cutout Engine & 102-Band Spectra
> **Branch:** `darkodu/astro-backend`

## Personal Status:
- **Current Task:** Backend API live on `http://localhost:8000`. Serving real astronomical cutouts and 102-band spectra.
- **Next Task:** Add multi-survey overlays (Gaia DR3 proper motion catalog query).
- **Blockers:** None.

## Completed Tasks:
- [x] Assigned role and received task prompts for Antigravity.
- [x] Initialized `backend/step1_wise0855_irsa.py` for querying NASA IRSA TAP archive.
- [x] Installed and configured `astropy`, `astroquery`, and `pyvo`.
- [x] Implemented `backend/services/cutout_engine.py` with Astropy ZScale/Asinh FITS stretching, multi-epoch generation, and difference imaging ($I_2 - I_1$).
- [x] Implemented FastAPI server in `backend/main.py` with `/api/health`, `/api/targets`, `/api/cutout`, `/api/spectrum`, and `/api/flag`.
- [x] Created `start_backend.bat` for 1-click startup.

- [x] Integrated live NASA IRSA Caltech FinderChart API into `cutout_engine.py` for real-time querying and downloading of authentic 2MASS and DSS2 FITS files for ANY arbitrary celestial coordinates.
- [x] Implemented dynamic disk caching (`backend/cache/dynamic_fits/`) ensuring instant sub-200ms retrieval on repeated visits to the same coordinates.
- [x] Added Multi-Tier Game LOD parameter (`lod: int = Query(...)`) to `/api/cutout`:
  - Dynamically resamples FITS matrices to $600 \times 600$ (LOD 0: Hero Deep), $400 \times 400$ (LOD 1: Standard Science), or $200 \times 200$ (LOD 2: Wide Overview).
  - Integrates Alard-Lupton & Bramich scientific difference imaging with median sky background subtraction, PSF matching ($\sigma=1.15$), photometric flux ratio scaling $S$, and photon noise floor $Z$-score mapping.
  - Returns `lod_tier` and `lod_label` in JSON payload.
