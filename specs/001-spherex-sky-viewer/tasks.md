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
