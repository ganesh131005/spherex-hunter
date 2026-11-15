# 📚 SPHEREx Hunter Documentation Library

Welcome to the centralized documentation library for **SPHEREx Hunter** (Team RIP, NASA Space Apps Challenge 2026). This index organizes all technical, scientific, astronomical, and design documentation across the project.

---

## 🗺️ Quick Navigation by Domain

### 🐙 1. GitHub & Contribution
* 📘 [**GitHub Master Guide (Newbies & Pros)**](GITHUB_GUIDE.md) — Step-by-step GitHub tutorial for beginners + developer branch architecture.
* 🤝 [**Contributing Guidelines**](../CONTRIBUTING.md) — Multi-branch protocol, commit conventions, and Pull Request checklist.
* 🏛️ [**Project Constitution**](../.specify/memory/constitution.md) — Team invariants, zero-ghost-closure rules, and verification gates.

---

### 🖥️ 2. Frontend & Viewport Architecture
* 🎨 [**UI & Observatory Guide**](UI_GUIDE.md) — Complete walkthrough of WebGL FITS canvas, Blink Comparator HUD, and 102-band spectrum.
* 🔭 [**Viewport Design Specification**](viewport_design.md) — CAD-style viewport layout, coordinate deconfliction, and overlay matrix hygiene.
* 📊 [**Viewport Overhaul Status & Log**](viewport_status.md) — Record of canvas transform resets, bug remediations, and performance tests.
* 🐞 [**Frontend Issues & Fixes Log**](frontend_issues.md) — Bug fixes for popup menus, toolbars, and responsive scaling.

---

### 🛰️ 3. Backend, TAP & Scientific Data Engine
* 📡 [**API Contract Specification**](API_CONTRACT.md) — Complete endpoint documentation for FastAPI, NASA IRSA TAP, and Gaia DR3 queries.
* 🔍 [**API Contract Audit**](API_CONTRACT_AUDIT.md) — Validation of backend route contracts, parameters, and error handling.
* 🪐 [**SPHEREx DR1 Primer & Spectral Bands**](dr1_notes.md) — $0.75\text{--}5.0\,\mu\text{m}$ infrared channels, detector arrays, and resolution.
* ⏱️ [**Temporal Epoch Pairing**](epoch_pairing.md) — Baseline historical pairing from 2MASS (1999) to SPHEREx (2025).
* 📑 [**Data & Calibration Notes**](data_notes.md) — WCS astrometry, FITS header ingestion, and background flux subtraction.

---

### 🔬 4. Scientific Validation & Audit
* 🎯 [**Scientific Validation Benchmark**](validation.md) — Empirical validation of Planet X / brown dwarf motion, detection completeness ($m_{\text{AB}} \approx 17.3$), and false-positive rates.
* ⚖️ [**Validation Mathematical Audit**](validation_audit.md) — Formal audit of ZOGY difference imaging, SNR co-addition, and PSF convolution.
* 📜 [**Claims Audit & Defense**](claims_audit.md) — Rigorous line-by-line verification of all NASA challenge submission claims against source code.
* 📚 [**Scientific References & Citations**](references.md) — Academic papers (arXiv, ADS, IPAC) supporting our methods.

---

### 🏆 5. NASA Hackathon Submission & Deliverables
* 🎤 [**Hackathon Pitch Script & Deck Guide**](HACKATHON_PITCH.md) — 4-minute presentation narrative, slide sequence, and demo script.
* 📋 [**70-Item Master Evaluation Roadmap**](master_execution_roadmap.md) — Full judge criteria tracking across all 10 project categories.
* 🎯 [**Master NASA Challenge Checklist**](../NASA_SPHEREx_App_Challenge_Checklist.md) — End-to-end evaluation checklist scoring 100% green pass.
* 🏗️ [**Project Status & Execution Plan**](PROJECT_STATUS_AND_PLAN.md) — Milestones, sprint phases, and system health status.

---

### 📸 6. Visual Evidence & Screenshots Gallery
* 🖼️ [**WISE 0855 Observatory Blink**](screenshots/01_wise0855_observatory_blink.png) — Multi-epoch blink comparator showing cold brown dwarf proper motion.
* 🖼️ [**Scientific Validation Modal**](screenshots/02_scientific_validation_modal.png) — Benchmark metrics, completeness curve, and flight exposure Codex.
* 🖼️ [**CDS Aladin Lite All-Sky HiPS View**](screenshots/03_aladin_sky_hips_view.png) — Interactive Strasbourg HiPS all-sky context layer.
