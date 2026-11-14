# 🧠 Memory Log: iceodu (Image Math & AI Lead)
> **Role:** Difference Imaging, WCS Alignment & Anomaly Detection
> **Branch:** `iceodu/image-math-ai`

## Personal Status:
- **Current Task:** [Issue #15] Fix Gaia DR3 Blue Overlay Projection Mismatch & FOV Scale Discrepancy (WCS Gnomonic TAN Projection & Dynamic FOV Scaling).
- **Next Task:** Implement 6-array co-addition for 4x SNR boost.
- **Blockers:** None currently.

## Assigned GitHub Tasks:
- [ ] **[#15] [ASTROMETRY] Fix Gaia DR3 Overlay Projection Mismatch & FOV Scale Discrepancy** (https://github.com/joker0210G/spherex-hunter/issues/15)
  - Anchor `pixelsPerArcmin` dynamically to `activeImg.fov` or `camera.fov` (eliminate hardcoded `3.0'`).
  - Implement standard WCS Gnomonic Tangent projection (`projectSkyToTangentialArcmin`).
  - Back-propagate Gaia DR3 coordinates from epoch $J2016.0$ to survey observation dates ($t_{\text{obs}} \approx 1999.0 / 2025.5$).

## Completed Tasks:
- [x] Assigned role and received task prompts for Antigravity.
