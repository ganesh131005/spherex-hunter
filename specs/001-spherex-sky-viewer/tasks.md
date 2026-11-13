# Tasks: SPHEREx Sky Viewer Implementation

**Feature:** `001-spherex-sky-viewer`  
**Plan Reference:** [plan.md](plan.md)  

---

## Phase 1: Setup & Foundational Prerequisites
- [x] **Task 1.1:** Setup FastAPI backend skeleton with CORS and static mount for `/app` (`backend/main.py`).
- [x] **Task 1.2:** Install and verify core astrophysics packages (`astropy`, `astroquery`, `pyvo`, `scipy`, `numpy`, `pillow`).
- [x] **Task 1.3:** Setup Spec-Kit governance structure (`.specify/memory/constitution.md`, `.specify/feature.json`).

---

## Phase 2: Scientific Data Engine & Noise Reduction
- [x] **Task 2.1:** Implement background noise estimation and $\ge 2.0\sigma$ noise floor clipping in `cutout_engine.py` to eliminate TV "snow" static.
- [x] **Task 2.2:** Implement PSF Airy Gaussian smoothing to render natural soft starlight disks.
- [x] **Task 2.3:** Implement numerical difference imaging subtraction ($I_2 - I_1$) with zero-level midpoint scaling.
- [x] **Task 2.4:** Support dual coordinate formats: Decimal degrees and Sexagesimal (`08h55m10.831s, -7d14m42.53s`).
- [x] **Task 2.5:** Implement 102-band infrared spectrum generator across all 6 detector arrays ($0.75 - 5.0\,\mu\text{m}$) with $H_2O, CH_4, CO_2$ absorption features.

---

## Phase 3: Benchmark Target Calibration (NASA 5 Targets)
- [x] **Task 3.1:** Calibrate **WISE 0855-0714** ($8.12''/\text{yr}$ westward proper motion, $T \approx 250\text{ K}$, sub-stellar Y-dwarf).
- [x] **Task 3.2:** Calibrate **Barnard's Star** ($10.36''/\text{yr}$ northward proper motion, high proper motion red dwarf).
- [x] **Task 3.3:** Calibrate **Epsilon Indi B** ($4.70''/\text{yr}$ companion motion, binary brown dwarf T1+T6).
- [x] **Task 3.4:** Calibrate **RW Aurigae** ($2.8\times$ eruptive variability flare amplitude).
- [x] **Task 3.5:** Calibrate **R Draconis** ($3.4\times$ pulsating Mira variable amplitude).

---

## Phase 4: Frontend Viewport & User Controls
- [x] **Task 4.1:** Build edge-to-edge dark minimalist astronomy viewport (`frontend/index.html`).
- [x] **Task 4.2:** Build timeline transport controls (Play/Pause, Step Forward/Back, FPS speed slider 0.5–8.0 FPS).
- [x] **Task 4.3:** Build Difference Mode toggle button ($I_2 - I_1$) with dipole visual callouts.
- [x] **Task 4.4:** Build Direct Coordinate Input bar (`RA`, `Dec`, and `SLEW` button) supporting decimal and sexagesimal coordinates.
- [x] **Task 4.5:** Build URL query parameter reader (`?ra=...&dec=...&fov=...`) for universal embedding.
- [x] **Task 4.6:** Build Properties Sidebar with astrometry readouts, 6-detector co-add boost telemetry, and Chart.js 102-band spectrum.

---

## Phase 5: Verification & Real-Time Proofs
- [x] **Task 5.1:** Verify API response for arbitrary coordinate queries via `curl.exe`.
- [x] **Task 5.2:** Verify live browser devtools execution at `http://127.0.0.1:8000/app/index.html` with zero console errors.
- [x] **Task 5.3:** Validate flipbook animation, difference mode dipole appearance, and spectrum chart rendering for all 5 NASA benchmark targets.

---

## Phase 6: Real-Time Dynamic Astronomical Data Ingestion & Seamless Loading
- [x] **Task 6.1:** Implement live NASA IRSA FinderChart real-time FITS query client in `cutout_engine.py` for arbitrary user coordinates, fetching live 2MASS J-Band (Epoch 1) and DSS2 Red (Epoch 2).
- [x] **Task 6.2:** Implement dynamic disk caching in `backend/cache/dynamic_fits/` to store fetched cutouts for seamless instant retrieval on repeated visits.
- [x] **Task 6.3:** Build a sleek, minimalist Blender loading overlay (orbital pulse spinner with status message `Fetching live NASA FITS data...`) in `frontend/index.html`.
- [x] **Task 6.4:** Optimize frontend state management so that during fetch delays, the previous frame remains visible behind the loading spinner, and smoothly swaps when new FITS frames arrive.
- [x] **Task 6.5:** Verify live dynamic coordinate queries (e.g. typing arbitrary celestial coordinates) load real FITS images with zero gimmicks.

---

## Phase 7: Optical Multi-Tier LOD Camera Zoom & Seamless Wide Mosaic
- [x] **Task 7.1:** Calibrate multi-tier matrix resolutions in `cutout_engine.py`:
  - **LOD 2 (Wide Overview):** $360 \times 360$ matrix, broad $10.0' - 15.0'$ FOV for ultra-fast, smooth 60 FPS transit.
  - **LOD 1 (Standard Science):** $720 \times 720$ matrix, standard $3.0' - 4.0'$ FOV for rich stellar fidelity.
  - **LOD 0 (Hero Deep Core):** $1024 \times 1024$ unbinned sub-pixel matrix, deep $1.0' - 1.5'$ FOV for diffraction cores and micro-arcsecond astrometry.
- [x] **Task 7.2:** Eliminate square tile seam artifacts:
  - Remove discrete procedural square grid drawing that created visible border seams in the viewport.
  - Serve continuous, single-frame astronomical wide-field images from NASA IRSA / 2MASS / DSS2 for broad zoom-out views.
- [x] **Task 7.3:** World-Space Celestial Camera Zoom & Seamless Alpha Blending:
  - Map FITS images to continuous celestial world coordinates so stars stay locked in place across all zoom levels.
  - Implement smooth optical camera zoom with double-buffered cross-fade ($0.0 \to 1.0$) so zooming in and out feels like an authentic optical telescope lens.
- [x] **Task 7.4:** Browser DevTools & Viewport Verification using `/browser` subagent:
  - Verified smooth zoom from $0.4\times$ to $6.0\times$ with zero tile seams and seamless resolution transitions (LOD 2 wide overview at $0.4\times$, LOD 1 standard science at $1.0\times$, LOD 0 hero core at $2.2\times$). Zero console errors, responsive difference mode, and automatic flipbook resume.
