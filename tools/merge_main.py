#!/usr/bin/env python3
"""
Automated merge & conflict resolution script for SPHEREx Hunter.
Merges origin/main into darkodu/astro-backend, cleanly reconciling all backend,
cutout engine, multi-survey, and frontend features.
"""

import os
import re
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(REPO_ROOT)

def run(cmd, check=True):
    print(f">> Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"FAILED (code {res.returncode}): {res.stderr}\n{res.stdout}")
    return res

def resolve_cutout_engine():
    path = os.path.join("backend", "services", "cutout_engine.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Marker 1: Optional
    content = re.sub(
        r'<<<<<<< HEAD\n=======\nfrom typing import Optional\n>>>>>>> origin/main',
        'from typing import Optional',
        content
    )

    # Marker 2: preprocessing import & benchmark comment
    m2_repl = (
        'from backend.science.preprocessing import preprocess_spherex_hdu\n\n'
        '# Benchmark target bookmarks. Only literature-sourced astrometry / classification lives here:\n'
        '# coordinates (SIMBAD ICRS), proper motion (Gaia DR3 / Luhman 2014), nominal effective temperature.\n'
        '# Per-target "telemetry" (W1-W2 colour, Gaia match status, contamination flags, NEOSSat status)\n'
        '# is NOT hardcoded: it must come from a live archive query or be reported as unavailable.'
    )
    content = re.sub(
        r'<<<<<<< HEAD\nfrom backend\.science\.preprocessing import preprocess_spherex_hdu\n\n=======\n\n# Benchmark target bookmarks.*?\n>>>>>>> origin/main',
        m2_repl,
        content,
        flags=re.DOTALL
    )

    # Marker 3: get_102_band_spectrum return dict
    m3_repl = (
        '        "flux_microjanskys": flux_out,\n'
        '        "flux_units": flux_units,\n'
        '        "bands": bands,\n'
        '        "array_summary": array_summary,\n'
        '        "array_counts": array_counts,\n'
        '        "observation_dates": obs_dates,\n'
        '        "simultaneity_notice": "Spectra assembled from different dates across the 6 arrays are not simultaneous for variable stars.",'
    )
    content = re.sub(
        r'<<<<<<< HEAD\n        "flux_microjanskys": flux,\n        "observation_dates": obs_dates,\n        "simultaneity_notice": ".*?"\n=======\n        "flux_microjanskys": flux_out,\n        "flux_units": flux_units,\n        "bands": bands,\n        "array_summary": array_summary,\n        "array_counts": array_counts,\n>>>>>>> origin/main',
        m3_repl,
        content,
        flags=re.DOTALL
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    assert "<<<<<<<" not in content, "Conflict markers remain in cutout_engine.py"
    print("Resolved backend/services/cutout_engine.py successfully.")

def resolve_main_py():
    path = os.path.join("backend", "main.py")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Marker 1: Imports
    m1_repl = (
        'from fastapi.responses import FileResponse, JSONResponse, Response\n'
        'from fastapi.staticfiles import StaticFiles\n'
        'from pydantic import BaseModel\n\n'
        'from backend.api_v1 import make_request_id, router as api_v1_router\n'
        'from backend.models_v1 import ProblemDetails\n\n'
        'from backend.services.catalog_engine import (\n'
        '    crossmatch_photometry,\n'
        '    query_2mass_psc,\n'
        '    query_simbad_metadata,\n'
        '    query_spherex_archive,\n'
        '    query_wise_catalog,\n'
        ')'
    )
    content = re.sub(
        r'<<<<<<< HEAD\nfrom fastapi\.responses import JSONResponse, Response.*?from backend\.services\.catalog_engine import crossmatch_photometry, query_2mass_psc, query_simbad_metadata\n=======\nfrom fastapi\.responses import FileResponse, Response.*?query_wise_catalog,\n\)\n>>>>>>> origin/main',
        m1_repl,
        content,
        flags=re.DOTALL
    )

    # Marker 2: Endpoints (/api/cutout/raw, /api/cutout/raw/header, /api/observations)
    m2_repl = (
        '@app.get("/api/cutout/raw")\n'
        'def get_cutout_raw_compat(\n'
        '    request: Request,\n'
        '    target: str = Query(..., description="Target slug e.g. \'sample_leo\' or \'wise0855\'"),\n'
        '    format: Optional[str] = Query("binary", description="\'binary\' or \'header\'")\n'
        '):\n'
        '    """Exposes Float32 ArrayBuffer cutout streaming for dynamic client-side stretch sliders."""\n'
        '    from backend.api_v1 import get_cutout_raw\n'
        '    return get_cutout_raw(request=request, target=target, format=format)\n\n'
        '@app.get("/api/cutout/raw/header")\n'
        'def get_cutout_raw_header_compat(\n'
        '    request: Request,\n'
        '    target: str = Query(..., description="Target slug e.g. \'sample_leo\' or \'wise0855\'")\n'
        '):\n'
        '    """Exposes JSON WCS header for raw float32 cutout."""\n'
        '    from backend.api_v1 import get_cutout_raw_header\n'
        '    return get_cutout_raw_header(request=request, target=target)\n\n'
        '@app.get("/api/observations")\n'
        'def get_available_observations(\n'
        '    ra: str = Query(..., description="Right Ascension in decimal deg or sexagesimal"),\n'
        '    dec: str = Query(..., description="Declination in decimal deg or sexagesimal"),\n'
        '    start_date: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"),\n'
        '    end_date: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"),\n'
        '):\n'
        '    """\n'
        '    Returns authentic multi-epoch observation metadata covering celestial coordinates (RA, Dec)\n'
        '    within an optional temporal date/time filtering window [start_date, end_date].\n'
        '    """\n'
        '    try:\n'
        '        ra_deg, dec_deg = parse_celestial_coords(ra, dec)\n'
        '        return query_observation_timeline(ra_deg, dec_deg, start_date=start_date, end_date=end_date)\n'
        '    except HTTPException:\n'
        '        raise\n'
        '    except Exception as e:\n'
        '        raise HTTPException(status_code=500, detail=str(e))'
    )
    content = re.sub(
        r'<<<<<<< HEAD\n@app\.get\("/api/cutout/raw"\).*?return get_cutout_raw_header\(request=request, target=target\)\n=======\n@app\.get\("/api/observations"\).*?raise HTTPException\(status_code=500, detail=str\(e\)\)\n>>>>>>> origin/main',
        m2_repl,
        content,
        flags=re.DOTALL
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    assert "<<<<<<<" not in content, "Conflict markers remain in backend/main.py"
    print("Resolved backend/main.py successfully.")

def resolve_candidate_discoveries():
    path = os.path.join("07 - Team Memory & Sync", "candidate_discoveries.json")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    m_repl = (
        '  {\n'
        '    "candidate_id": "SPX-2026-6A23DC",\n'
        '    "target_id": "sample_leo",\n'
        '    "target_name": "Technical Validation Field (SPHEREx D6 Flight Pair)",\n'
        '    "ra": 160.605,\n'
        '    "dec": 30.702,\n'
        '    "object_type": "mover",\n'
        '    "category": "mover",\n'
        '    "user_handle": "@pytest_runner",\n'
        '    "notes": "Fast-moving candidate tracklet test",\n'
        '    "timestamp": "2026-11-14T10:38:53.092291+00:00"\n'
        '  },\n'
        '  {\n'
        '    "candidate_id": "SPX-2026-RWAUR",\n'
        '    "target_name": "RW Aurigae A/B",\n'
        '    "candidate_name": "RW Aurigae A/B",\n'
        '    "ra": 76.95642,\n'
        '    "dec": 30.40142,\n'
        '    "object_type": "Eruptive T-Tauri Variable",\n'
        '    "motion_type": "Eruptive T-Tauri Variable",\n'
        '    "proper_motion_mas": 16.5,\n'
        '    "user_handle": "AAVSO / SPHEREx Transient Alert",\n'
        '    "astronomer": "AAVSO / SPHEREx Transient Alert",\n'
        '    "confidence": 5,\n'
        '    "notes": "Young stellar object with circumstellar disk dimming and infrared excess.",\n'
        '    "timestamp": "2026-11-12T22:00:00Z",\n'
        '    "scientific_validation": {\n'
        '      "is_ultracold_candidate": false,\n'
        '      "optical_infrared_g_minus_ks": 3.4,\n'
        '      "simbad_counterpart": "V* RW Aur",\n'
        '      "spectral_classification": "K1-K4Ve",\n'
        '      "verification_status": "CONFIRMED_VARIABLE"\n'
        '    }\n'
        '  }'
    )

    content = re.sub(
        r'  {\n<<<<<<< HEAD\n    "ra": 133\.79513,.*?>>>>>>> origin/main\n  }',
        m_repl,
        content,
        flags=re.DOTALL
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    assert "<<<<<<<" not in content, "Conflict markers remain in candidate_discoveries.json"
    print("Resolved candidate_discoveries.json successfully.")

def resolve_shared_project_state():
    path = os.path.join("07 - Team Memory & Sync", "SHARED_PROJECT_STATE.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    m1 = (
        '| **Astro-Data / Backend** | `darkodu` | `darkodu/astro-backend` | DR1 HiPS Context Layer, Provenance Alignment & Cross-Survey Pairs | 🟢 100% Operational |\n'
        '| **Frontend / Blink UI** | `coolodu` | `coolodu/web-frontend` | Integrated `darkodu/astro-backend` + Observatory UI + 35-Note Vault | 🟢 Live / Verified |'
    )
    pattern1 = r'<<<<<<< HEAD\n\| \*\*Astro-Data / Backend\*\*.*?\n>>>>>>> origin/main'
    text = re.sub(pattern1, m1, text, flags=re.DOTALL)

    m2_match = re.search(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/main', text, flags=re.DOTALL)
    if m2_match:
        head_part = m2_match.group(1).strip()
        orig_part = m2_match.group(2).strip()
        combined = head_part + '\n\n' + orig_part
        text = text[:m2_match.start()] + combined + text[m2_match.end():]

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    assert "<<<<<<<" not in text, "Conflict markers remain in SHARED_PROJECT_STATE.md"
    print("Resolved SHARED_PROJECT_STATE.md successfully.")

def resolve_frontend_index():
    path = os.path.join("frontend", "index.html")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pairs = []
    curr_start = None
    curr_sep = None
    for i, l in enumerate(lines):
        if l.startswith("<<<<<<<"):
            curr_start = i
        elif l.startswith("======="):
            curr_sep = i
        elif l.startswith(">>>>>>>"):
            pairs.append((curr_start, curr_sep, i))

    print(f"Resolving {len(pairs)} conflict blocks in frontend/index.html...")

    # We will build output lines chunk by chunk
    out_lines = []
    last_idx = 0

    for idx, (s, m, e) in enumerate(pairs):
        out_lines.extend(lines[last_idx:s])
        head_chunk = "".join(lines[s+1:m])
        orig_chunk = "".join(lines[m+1:e])

        if idx == 0:  # Favicon
            out_lines.append('  <link rel="icon" type="image/svg+xml" href="/app/assets/logo.svg">\n')
        elif idx == 1:  # App Brand & Logo
            out_lines.append(
                '      <!-- App Brand & Logo -->\n'
                '      <div class="flex items-center gap-2.5 pr-3 border-r border-space-700 cursor-pointer group" id="btnHeaderBrand" title="SPHEREx Hunter: Deep Space Infrared Observatory. Click to open Mission Tour.">\n'
                '        <a href="#" id="brandLogoLink" class="w-8 h-8 rounded-lg bg-space-950 border border-space-700 flex items-center justify-center relative shadow-md shadow-orange-950/40 group-hover:border-blender-orange transition-all">\n'
                '          <img src="/app/assets/logo.svg" alt="SPHEREx Hunter Logo" class="w-6 h-6 object-contain drop-shadow-[0_0_6px_rgba(234,118,0,0.5)] transition-transform group-hover:scale-110" />\n'
                '        </a>\n'
                '        <div class="flex flex-col">\n'
                '          <div class="flex items-baseline gap-1">\n'
                '            <span class="font-bold text-white tracking-wide text-sm font-sans">SPHEREx</span>\n'
                '            <span class="text-blender-orange font-bold text-xs tracking-wider">HUNTER</span>\n'
                '          </div>\n'
                '          <span class="text-[9px] text-gray-400 font-mono hidden xl:inline leading-none">102-Band NASA IR Observatory</span>\n'
                '        </div>\n'
                '      </div>\n'
            )
        elif idx == 2:  # Popover title
            out_lines.append(
                '        <div id="coordsPopover" class="hidden absolute right-0 top-10 mt-1 w-80 bg-space-900 border border-space-700 rounded-lg p-3.5 shadow-2xl z-50 space-y-3 font-mono">\n'
                '          <div class="flex items-center justify-between pb-1.5 border-b border-space-700">\n'
                '            <span class="text-xs font-bold text-white flex items-center gap-1.5">\n'
                '              <i data-lucide="navigation" class="w-3.5 h-3.5 text-cyan-400"></i>\n'
                '              <span>Celestial Coordinates & FOV</span>\n'
                '            </span>\n'
                '            <button id="btnCloseCoords" class="text-gray-400 hover:text-white text-xs">✕</button>\n'
                '          </div>\n'
            )
        elif idx == 3:  # Format hint and RA input with validation hint
            out_lines.append(
                '          <!-- Format Hint -->\n'
                '          <div class="bg-space-950 p-2 rounded border border-space-800 text-[10px] text-gray-400 space-y-0.5">\n'
                '            <div class="text-cyan-400 font-semibold flex items-center gap-1">\n'
                '              <i data-lucide="help-circle" class="w-3 h-3"></i>\n'
                '              <span>Accepted Formats:</span>\n'
                '            </div>\n'
                '            <div>• Decimal: <span class="text-white">133.79513, -7.24515</span></div>\n'
                '            <div>• Sexagesimal: <span class="text-white">08h55m10.83s, -07d14m42.5s</span></div>\n'
                '          </div>\n\n'
                '          <div class="space-y-2 text-xs">\n'
                '            <div>\n'
                '              <div class="flex items-center justify-between mb-0.5">\n'
                '                <label class="block text-[10px] text-gray-400 font-sans">Right Ascension α (Sky Longitude):</label>\n'
                '                <span id="raValidationHint" class="text-[9px] text-gray-400 font-sans">0° to 360°</span>\n'
                '              </div>\n'
                '              <input id="inputRA" type="text" value="133.79513" placeholder="e.g. 133.79513° or 08h55m10.8s" class="w-full bg-space-950 border border-space-700 rounded px-2 py-1 text-white font-mono text-xs focus:border-blender-blue focus:outline-none transition" />\n'
                '            </div>\n'
            )
        elif idx == 4:  # Dec input
            out_lines.append(
                '            <div>\n'
                '              <div class="flex items-center justify-between mb-0.5">\n'
                '                <label class="block text-[10px] text-gray-400 font-sans">Declination δ (Sky Latitude):</label>\n'
                '                <span id="decValidationHint" class="text-[9px] text-gray-400 font-sans">-90° to +90°</span>\n'
                '              </div>\n'
                '              <input id="inputDec" type="text" value="-7.24515" placeholder="e.g. -7.24515° or -07d14m42.5s" class="w-full bg-space-950 border border-space-700 rounded px-2 py-1 text-white font-mono text-xs focus:border-blender-blue focus:outline-none transition" />\n'
                '            </div>\n'
            )
        elif idx == 5:  # FOV select
            out_lines.append(
                '            <div>\n'
                '              <div class="flex items-center justify-between mb-0.5">\n'
                '                <label class="block text-[10px] text-gray-400 font-sans">Field of View (Sky Zoom):</label>\n'
                '                <span class="text-[9px] text-amber-400 cursor-help" title="Field of View (Sky Zoom): Angular diameter in arcminutes (1\' = 1/60th deg). Full Moon is ~30\' wide, so 3.0\' is 1/10th the width of the full Moon.">1/10th Moon Width ⓘ</span>\n'
                '              </div>\n'
                '              <select id="selectFOV" class="w-full bg-space-950 border border-space-700 rounded px-2 py-1 text-white font-mono text-xs focus:border-blender-blue focus:outline-none transition">\n'
                '                <option value="1.0">1.0\' (Deep Core - Micro-Arcsec Dipoles)</option>\n'
                '                <option value="3.0" selected>3.0\' (Standard Field - 1/10th Moon)</option>\n'
                '                <option value="5.0">5.0\' (Medium Field - Cluster Context)</option>\n'
                '                <option value="10.0">10.0\' (Wide Overview - 1/3rd Moon)</option>\n'
                '                <option value="15.0">15.0\' (Max Field - Half Moon Width)</option>\n'
                '              </select>\n'
                '            </div>\n'
                '          </div>\n'
            )
        elif idx == 6:  # 1-Click Sky landmarks presets
            out_lines.append(
                '          <!-- Quick Sky Landmarks Presets -->\n'
                '          <div class="border-t border-space-800 pt-2 space-y-1">\n'
                '            <span class="text-[10px] text-gray-400 font-semibold uppercase tracking-wider block">1-Click Sky Landmarks:</span>\n'
                '            <div class="grid grid-cols-2 gap-1 text-[10px]">\n'
                '              <button class="preset-coord-btn px-1.5 py-1 rounded bg-space-950 hover:bg-space-800 border border-space-800 text-left transition flex flex-col" data-ra="133.79513" data-dec="-7.24515" data-fov="3.0">\n'
                '                <span class="text-amber-400 font-bold truncate">WISE 0855</span>\n'
                '                <span class="text-gray-500 text-[9px]">Cold Brown Dwarf</span>\n'
                '              </button>\n'
                '              <button class="preset-coord-btn px-1.5 py-1 rounded bg-space-950 hover:bg-space-800 border border-space-800 text-left transition flex flex-col" data-ra="269.45208" data-dec="4.69339" data-fov="3.0">\n'
                '                <span class="text-amber-400 font-bold truncate">Barnard\'s Star</span>\n'
                '                <span class="text-gray-500 text-[9px]">High Proper Motion</span>\n'
                '              </button>\n'
                '              <button class="preset-coord-btn px-1.5 py-1 rounded bg-space-950 hover:bg-space-800 border border-space-800 text-left transition flex flex-col" data-ra="83.82208" data-dec="-5.39111" data-fov="5.0">\n'
                '                <span class="text-cyan-400 font-bold truncate">Orion Nebula</span>\n'
                '                <span class="text-gray-500 text-[9px]">Star Forming Region</span>\n'
                '              </button>\n'
                '              <button class="preset-coord-btn px-1.5 py-1 rounded bg-space-950 hover:bg-space-800 border border-space-800 text-left transition flex flex-col" data-ra="266.41684" data-dec="-29.00781" data-fov="3.0">\n'
                '                <span class="text-purple-400 font-bold truncate">Sgr A* (Galactic Core)</span>\n'
                '                <span class="text-gray-500 text-[9px]">Supermassive Black Hole</span>\n'
                '              </button>\n'
                '              <button class="preset-coord-btn px-1.5 py-1 rounded bg-space-950 hover:bg-space-800 border border-space-800 text-left transition flex flex-col" data-ra="331.04379" data-dec="-56.78272" data-fov="3.0">\n'
                '                <span class="text-cyan-400 font-bold truncate">Epsilon Indi B</span>\n'
                '                <span class="text-gray-500 text-[9px]">Binary Brown Dwarf</span>\n'
                '              </button>\n'
                '              <button class="preset-coord-btn px-1.5 py-1 rounded bg-space-950 hover:bg-space-800 border border-space-800 text-left transition flex flex-col" data-ra="346.62208" data-dec="-5.04139" data-fov="3.0">\n'
                '                <span class="text-emerald-400 font-bold truncate">Trappist-1</span>\n'
                '                <span class="text-gray-500 text-[9px]">7 Exoplanet System</span>\n'
                '              </button>\n'
                '            </div>\n'
                '          </div>\n\n'
                '          <button id="btnGoCoords" class="w-full py-1.5 rounded bg-blender-orange hover:bg-orange-600 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition shadow">\n'
                '            <i data-lucide="compass" class="w-3.5 h-3.5"></i>\n'
                '            <span>Slew Telescope & Fetch Live Sky</span>\n'
                '          </button>\n'
            )
        elif idx == 7:  # Direct Fetch button
            out_lines.append(
                '      <!-- Primary Action: Direct Fetch Button (Issue #6) -->\n'
                '      <button id="btnTopFetch" class="px-3 py-1 rounded bg-blender-orange hover:bg-orange-600 text-white font-semibold text-xs flex items-center gap-1.5 shadow transition" title="Query NASA IRSA: Fetch real calibrated FITS cutouts from NASA archives (Enter)">\n'
                '        <i data-lucide="download" class="w-3.5 h-3.5"></i>\n'
                '        <span id="btnTopFetchLabel">Fetch Sky Tile</span>\n'
                '      </button>\n'
            )
        elif idx == 8:  # Multi-Survey IR synthesis card before Section 6
            out_lines.append(
                '        <!-- WISE, 2MASS & SPHEREx Multi-Survey IR Synthesis Card -->\n'
                '        <div class="bg-space-950/70 p-3 rounded-lg border border-space-700 space-y-1.5 text-[11px]">\n'
                '          <div class="text-amber-400 font-bold flex items-center gap-1.5">\n'
                '            <i data-lucide="layers" class="w-3.5 h-3.5"></i>\n'
                '            <span>Multi-Survey Astrometric Synthesis</span>\n'
                '          </div>\n'
                '          <div class="text-gray-300 text-[10px] leading-relaxed">\n'
                '            Target crossmatched against <span class="text-cyan-300">Gaia DR3</span>, <span class="text-cyan-300">2MASS</span> (J/H/Ks), and <span class="text-cyan-300">AllWISE</span> (W1/W2/W3/W4) archives to assemble physical SEDs and calculate true space motion vectors.\n'
                '          </div>\n'
                '        </div>\n\n'
                '        <!-- SECTION 6: EXTERNAL ARCHIVAL BRIDGES & ACTIONS -->\n'
            )
        elif idx == 9:  # coaddArrayStatus
            out_lines.append('          <span id="coaddArrayStatus" class="text-gray-400 text-[10px]">Awaiting Flight Co-adds</span>\n')
        elif idx == 10:  # SPHEREx 6 detector array cards
            out_lines.append(orig_chunk)
        elif idx == 11:  # Dock Spectrum Panel (honesty notice + 6 array tabs + stepper + canvas)
            out_lines.append(
                '      <!-- PANEL 2: SPECTRUM (102-Band SPHEREx Spectrophotometry with 6-Array Selector & 17-Wavelength Stepper) -->\n'
                '      <div id="dockPanelSpectrum" class="h-full hidden px-3 py-1.5 flex flex-col justify-between gap-1">\n'
                '        <!-- Honesty Notice: Multi-Epoch Non-Simultaneity Disclaimer -->\n'
                '        <div id="spectrumNonSimultaneousNotice" class="hidden flex items-center justify-between bg-amber-950/60 border border-amber-600/60 px-2 py-0.5 rounded text-[10px] text-amber-200 font-mono">\n'
                '          <div class="flex items-center gap-1.5">\n'
                '            <span class="text-amber-400">⚠️</span>\n'
                '            <span>Non-simultaneous spectrum: SPHEREx scans across 6 LVF arrays at different observational epochs.</span>\n'
                '          </div>\n'
                '          <span class="text-[9px] text-amber-400">MJD 60789 - 60840</span>\n'
                '        </div>\n\n'
                '        <!-- Top Controls: 6-Array Tabs & 17-Channel Stepper (Issue #7) -->\n'
                '        <div class="flex items-center justify-between gap-2 shrink-0 border-b border-space-800 pb-1 text-[11px] font-mono flex-wrap">\n'
                '          <!-- 6-Array Tabs -->\n'
                '          <div class="flex items-center gap-1" id="arrayTabsContainer">\n'
                '            <span class="text-[10px] text-gray-400 uppercase font-sans font-semibold mr-1">Array:</span>\n'
                '            <button class="array-tab blender-btn blender-btn-active px-2 py-0.5 rounded text-[10px] transition" data-array="A1" title="A1: 0.75-1.11 µm (Optical boundary, stellar continuum)">A1</button>\n'
                '            <button class="array-tab blender-btn px-2 py-0.5 rounded text-[10px] transition" data-array="A2" title="A2: 1.11-1.64 µm (2MASS J/H overlap, photospheres)">A2</button>\n'
                '            <button class="array-tab blender-btn px-2 py-0.5 rounded text-[10px] transition" data-array="A3" title="A3: 1.64-2.42 µm (2MASS Ks overlap, circumstellar dust)">A3</button>\n'
                '            <button class="array-tab blender-btn px-2 py-0.5 rounded text-[10px] transition text-amber-300" data-array="A4" title="A4: 2.42-3.82 µm (H₂O Ice 3.05 µm, CH₄ 3.30 µm)">A4 🔬</button>\n'
                '            <button class="array-tab blender-btn px-2 py-0.5 rounded text-[10px] transition text-orange-300" data-array="A5" title="A5: 3.82-4.42 µm (CO₂ Ice 4.27 µm, Planet X thermal peak)">A5 🔬</button>\n'
                '            <button class="array-tab blender-btn px-2 py-0.5 rounded text-[10px] transition text-rose-300" data-array="A6" title="A6: 4.42-5.00 µm (CO 4.67 µm, Organics)">A6 🔬</button>\n'
                '          </div>\n\n'
                '          <!-- 17-Wavelength Stepper within Array -->\n'
                '          <div class="flex items-center gap-1.5 bg-space-950 px-2 py-0.5 rounded border border-space-800 shadow-inner">\n'
                '            <button id="chanPrev" class="blender-btn px-1.5 py-0.2 rounded hover:text-white" title="Previous Spectral Channel (Left Arrow)">◀</button>\n'
                '            <span id="chanDisplay" class="text-white font-semibold text-[10px] min-w-[150px] text-center">Ch 1 / 17 — λ = 0.750 µm</span>\n'
                '            <button id="chanNext" class="blender-btn px-1.5 py-0.2 rounded hover:text-white" title="Next Spectral Channel (Right Arrow)">▶</button>\n'
                '            <input type="range" id="chanSlider" min="1" max="17" value="1" class="w-20 h-1.5 bg-space-700 rounded cursor-pointer accent-amber-500">\n'
                '            <span id="chanFluxBadge" class="text-amber-400 font-mono text-[9px]">1.00 rel</span>\n'
                '          </div>\n\n'
                '          <!-- 102-Band Science Explainer Trigger -->\n'
                '          <button id="btnOpenBandScience" class="flex items-center gap-1 px-2 py-0.5 rounded bg-space-850 hover:bg-space-800 border border-space-700 text-cyan-300 hover:text-white transition text-[10px]" title="Open SPHEREx 102-Band Science Explainer Modal">\n'
                '            <i data-lucide="info" class="w-3 h-3 text-cyan-400"></i>\n'
                '            <span>102-Band Science</span>\n'
                '          </button>\n'
                '        </div>\n\n'
                '        <!-- Middle: Canvas & Molecular Absorption Legend -->\n'
                '        <div class="flex-1 flex items-center gap-3 min-h-0 relative">\n'
                '          <div class="flex-1 h-full relative">\n'
                '            <canvas id="spectrumChart"></canvas>\n'
                '          </div>\n'
                '          <!-- Molecular Reference Sidebar -->\n'
                '          <div class="w-52 bg-space-950 p-2 rounded border border-space-800 font-mono text-[9px] space-y-1 shrink-0 shadow-inner">\n'
                '            <div class="text-gray-400 font-bold uppercase text-[9px] text-cyan-400 border-b border-space-800 pb-0.5 flex justify-between">\n'
                '              <span>Molecular Signatures</span>\n'
                '              <span class="text-gray-500 font-normal">λ (µm)</span>\n'
                '            </div>\n'
                '            <div class="flex justify-between items-center"><span class="text-sky-400 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-sky-400 inline-block"></span>H₂O / Vapor:</span><span class="text-gray-300 font-bold">1.40 µm</span></div>\n'
                '            <div class="flex justify-between items-center"><span class="text-sky-300 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-sky-300 inline-block"></span>H₂O Ice:</span><span class="text-gray-300 font-bold">3.05 µm</span></div>\n'
                '            <div class="flex justify-between items-center"><span class="text-emerald-400 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>CH₄ Methane:</span><span class="text-gray-300 font-bold">3.30 µm</span></div>\n'
                '            <div class="flex justify-between items-center"><span class="text-orange-400 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-orange-400 inline-block"></span>CO₂ Ice:</span><span class="text-gray-300 font-bold">4.27 µm</span></div>\n'
                '            <div class="flex justify-between items-center"><span class="text-rose-400 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-rose-400 inline-block"></span>CO Monoxide:</span><span class="text-gray-300 font-bold">4.67 µm</span></div>\n'
                '          </div>\n'
                '        </div>\n'
            )
        elif idx == 12:  # Ambient stars & feathered image functions
            out_lines.append(orig_chunk)
        elif idx == 13:  # Viewport zoom & pixel calibration
            out_lines.append(
                '      // Ambient celestial background (continuous subtle starfield outside cutout to eliminate black void)\n'
                '      if (!diffMode) {\n'
                '        drawAmbientSkyBackground(ctx, w, h);\n'
                '      }\n\n'
                '      const activeImg = diffMode ? realDiffImg : (currentFrame === 1 ? realEpoch1Img : realEpoch2Img);\n'
                '      const currentTileFov = (activeImg && activeImg.fov) ? activeImg.fov : (camera.fov || 3.0);\n'
                '      const basePx = Math.min(w, h) * 0.90;\n'
                '      const pixelsPerArcmin = basePx / currentTileFov;\n'
                '      const cosDec = Math.cos(camera.dec * Math.PI / 180.0);\n'
            )
        elif idx == 14:  # Unified Multi-Resolution field (HEAD)
            out_lines.append(head_chunk)
        elif idx == 15:  # Auto-Identification overlay (HEAD)
            out_lines.append(head_chunk)
        elif idx == 16:  # getCurrentCoordinates
            out_lines.append(
                '    function getCurrentCoordinates() {\n'
                '      if (typeof canvasToSkyCoordinates === "function" && canvas && canvas.width > 0 && canvas.height > 0) {\n'
                '        return canvasToSkyCoordinates(canvas.width / 2, canvas.height / 2);\n'
                '      }\n'
                '      return { ra: camera.ra, dec: camera.dec };\n'
                '    }\n'
            )
        elif idx == 17:  # Spectrum variable declarations
            out_lines.append(
                '    let currentSpectrumDates = [];\n' + orig_chunk
            )
        elif idx == 18:  # Chart labels & plugin
            out_lines.append(orig_chunk)
        elif idx == 19:  # Scales
            out_lines.append(orig_chunk)
        elif idx == 20:  # Tooltips (with observation dates from HEAD)
            out_lines.append(
                '                title: (items) => `λ = ${items[0].label} µm`,\n'
                '                label: (item) => {\n'
                '                  if (item.datasetIndex === 1) {\n'
                '                    const meta = spectrumPointMeta[item.dataIndex];\n'
                '                    return meta ? `${meta.band}: ${meta.flux_ujy} µJy (${meta.mag} mag)` : `Catalog Flux: ${item.raw} µJy`;\n'
                '                  }\n'
                '                  return `SED Flux: ${item.raw} µJy`;\n'
                '                },\n'
                '                afterLabel: function (item) {\n'
                '                  const dateStr = currentSpectrumDates[item.dataIndex];\n'
                '                  return dateStr ? `Obs Date: ${dateStr}` : "";\n'
                '                }\n'
            )
        elif idx == 21:  # Tab click bindings & summary cards
            out_lines.append(orig_chunk)
        elif idx == 22:  # spec data setter
            out_lines.append(
                '          currentSpectrumData = spec;\n'
                '          currentSpectrumDates = spec.observation_dates || [];\n'
                '          updateArraySummaryCards(spec);\n'
            )
        elif idx == 23:  # scatterOverlay
            out_lines.append(orig_chunk)
        elif idx == 24:  # specChart update
            out_lines.append(orig_chunk)
        elif idx == 25:  # Gaia hover hit test (proper motion projection)
            out_lines.append(orig_chunk)
        elif idx == 26:  # URL & Hash parameter hydration
            out_lines.append(
                '      // Check URL & Hash parameters (Issue #12 Deep-Link Hub)\n'
                '      let urlParams = new URLSearchParams(window.location.search);\n'
                '      if (!urlParams.has("ra") && !urlParams.has("target") && !urlParams.has("mode") && window.location.hash) {\n'
                '        const hashStr = window.location.hash.replace(/^#/, "");\n'
                '        urlParams = new URLSearchParams(hashStr);\n'
                '      }\n'
            )
        elif idx == 27:  # start_date, end_date hydration
            out_lines.append(orig_chunk)
        elif idx == 28:  # mode parameter hydration
            out_lines.append(
                '        const lowerMode = paramMode.toLowerCase();\n'
                '        setTimeout(() => {\n'
                '          if (lowerMode === "diff" && document.getElementById("wsDiff")) {\n'
                '            document.getElementById("wsDiff").click();\n'
                '          } else if (lowerMode === "spec" && document.getElementById("wsSpec")) {\n'
                '            document.getElementById("wsSpec").click();\n'
                '          } else if (lowerMode === "hips" && document.getElementById("wsHipsMap")) {\n'
                '            document.getElementById("wsHipsMap").click();\n'
                '          } else if (lowerMode === "split" && document.getElementById("wsSplit")) {\n'
                '            document.getElementById("wsSplit").click();\n'
                '          }\n'
                '        }, 600);\n'
            )
        elif idx == 29:  # Modals (Onboarding tour, 102-band modal, share modal, command palette)
            out_lines.append(orig_chunk)
        else:
            out_lines.append(orig_chunk)

        last_idx = e + 1

    out_lines.extend(lines[last_idx:])
    resolved_text = "".join(out_lines)

    with open(path, "w", encoding="utf-8") as f:
        f.write(resolved_text)

    assert "<<<<<<<" not in resolved_text, "Conflict markers remain in frontend/index.html"
    print("Resolved frontend/index.html successfully.")

def main():
    print("Starting automated merge of origin/main into darkodu/astro-backend...")
    # Fetch origin main
    run("git fetch origin main")

    # Start merge
    res = run("git merge origin/main", check=False)
    if res.returncode == 0:
        print("Merged cleanly without conflicts.")
        return

    print("Resolving merge conflicts...")

    # Checkout origin/main for docs, test files, logo, tools, bat
    run('git checkout --theirs "05 - Research & Resources/"')
    run('git checkout --theirs tests/test_aladin_hips_e2e.py tests/test_continuous_viewport_e2e.py tests/test_google_maps_spherex_e2e.py tests/test_issues_9_10_12_e2e.py tests/test_live_cutout_zogy.py tests/test_ui_brand_and_nav_e2e.py')
    run('git checkout --theirs frontend/assets/logo.svg')
    run('git checkout --theirs backend/models_v1.py')
    run('git checkout --theirs backend/services/gaia_service.py')
    run('git checkout --theirs tools/github_bridge.py')
    run('git checkout --theirs scripts/build_frontend.py')
    run('git checkout --theirs run_spherex_hunter.bat')

    # Checkout HEAD for authentic demo_cache, api_v1, neossat, verification
    run('git checkout --ours demo_cache/')
    run('git checkout --ours backend/api_v1.py')
    run('git checkout --ours backend/services/neossat_service.py backend/services/verification_service.py')

    # Reconcile code in cutout_engine, main, candidate_discoveries, shared_project_state, index.html
    resolve_cutout_engine()
    resolve_main_py()
    resolve_candidate_discoveries()
    resolve_shared_project_state()
    resolve_frontend_index()

    # Stage all resolved files
    run("git add -A")

    # Check git status
    status_res = run("git status --porcelain")
    unmerged = [l for l in status_res.stdout.splitlines() if l.startswith("UU") or l.startswith("AA") or l.startswith("DU") or l.startswith("UD")]
    if unmerged:
        print("ERROR: Unmerged files remain:")
        for u in unmerged:
            print("  ", u)
        sys.exit(1)

    print("All conflicts resolved! Committing merge...")
    commit_msg = "merge(darkodu): integrate origin/main and resolve conflicts with cutout engine, multi-survey SEDs, and 102-band spectrophotometry"
    run(f'git commit -m "{commit_msg}"')
    print("Merge committed successfully.")

if __name__ == "__main__":
    main()
