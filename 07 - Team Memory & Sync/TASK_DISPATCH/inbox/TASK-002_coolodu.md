---
task_id: TASK-002
title: Render Gaia DR3 and 2MASS Catalog Overlays on Blender Canvas
requested_by: darkodu
assigned_to: coolodu
type: hybrid
priority: HIGH
status: PENDING
created_at: 2026-11-13T15:18:45.435792
source_branch: coolodu/web-frontend
---

# Task: Render Gaia DR3 and 2MASS Catalog Overlays on Blender Canvas
> **Requester:** @darkodu | **Assigned To:** @coolodu
> **Resource Type:** `hybrid` | **Priority:** `HIGH`

## 📝 Objective & Brief:
The backend now serves live catalog endpoints on port 8000: 1. GET /api/catalog/gaia?ra={ra}&dec={dec}&radius={radius} (returns ESA Gaia DR3 sources with pmra_mas_yr, pmdec_mas_yr, total_pm_mas_yr, pm_angle_deg, parallax_mas, distance_pc, and offset_arcsec {dx, dy}); 2. GET /api/catalog/2mass (returns J, H, Ks photometry and ph_qual); 3. GET /api/catalog/crossmatch (returns unified optical-to-infrared color cross-match and is_ultracold_candidate flag). Please update frontend/index.html to add a toggle in the sidebar for [x] Gaia Motion Vectors, fetching /api/catalog/gaia and rendering vector arrows on the canvas over moving stars, with special dipole ring highlights for high proper motion sources.

## 🎯 Definition of Done:
- [ ] Task executed by @coolodu using optimal hardware/token capabilities.
- [ ] Output artifacts committed to branch `coolodu/web-frontend` or specified destination.
- [ ] Task marked as completed via `python tools/task_forwarder.py complete --task TASK-002`.
