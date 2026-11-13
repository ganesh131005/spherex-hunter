"""
🚀 SPHEREx Hunter - Diagnostic Test Suite for Astro-Data Engine
NASA Space Apps 2026 - Team RIP (darkodu)

Tests:
1. Benchmark Target Metadata Integrity
2. Astropy / FITS Cutout Engine & Multi-Tier LOD Pipeline (LOD 0, 1, 2)
3. Alard-Lupton Difference Imaging Math & Residual Z-scores
4. 102-Band Near-Infrared SPHEREx Spectroscopy (0.75 - 5.0 μm)
5. FastAPI REST API Route Handlers & Astropy Coordinate Parsing
"""

import time
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.cutout_engine import (
    BENCHMARKS,
    fetch_real_cutout,
    get_102_band_spectrum,
    compute_scientific_difference
)
from backend.main import (
    health_check,
    get_benchmark_targets,
    get_cutout,
    get_spectrum,
    get_gaia_catalog,
    parse_celestial_coords,
    flag_candidate,
    get_discoveries,
    DiscoveryCandidate
)
from backend.services.catalog_engine import query_gaia_dr3

def print_banner(text):
    print("\n" + "=" * 65)
    print(f"  {text}")
    print("=" * 65)

def test_benchmark_targets():
    print_banner("1. BENCHMARK TARGET METADATA VERIFICATION")
    required_benchmarks = ["wise0855", "barnard", "epsindi", "rwaur", "rdraconis"]
    for key in required_benchmarks:
        assert key in BENCHMARKS, f"Missing benchmark target: {key}"
        data = BENCHMARKS[key]
        print(f"  [OK] {data['name']:<22} | RA: {data['ra']:<9.4f} Dec: {data['dec']:<9.4f} | Type: {data['type']}")
    print(f"\nAll {len(required_benchmarks)} NASA benchmark targets validated successfully!")

def test_cutout_engine_lods():
    print_banner("2. ASTROPY CUTOUT ENGINE & LOD LATENCY TESTS")
    test_cases = [
        ("wise0855", "WISE 0855-0714 (Y-Dwarf Brown Dwarf)", 1),
        ("wise0855", "WISE 0855-0714 (LOD 0 Hero Deep)", 0),
        ("wise0855", "WISE 0855-0714 (LOD 2 Wide Overview)", 2),
        ("barnard", "Barnard's Star (Proper Motion Red Dwarf)", 1),
        ("rwaur", "RW Aurigae (Eruptive Variable)", 1),
    ]

    for target_key, label, lod in test_cases:
        target = BENCHMARKS[target_key]
        start_time = time.perf_counter()
        result = fetch_real_cutout(
            ra=target["ra"],
            dec=target["dec"],
            fov_arcmin=3.0,
            target_key=target_key,
            lod=lod
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Assertions
        assert result["status"] == "success"
        assert len(result["epochs"]) == 2
        assert "image_data" in result["epochs"][0]
        assert "image_data" in result["epochs"][1]
        assert "difference_image" in result
        assert result["lod_tier"] == lod

        img_len_kb = len(result["epochs"][0]["image_data"]) / 1024
        print(f"  [PASS] {label:<42} | LOD: {lod} | Latency: {elapsed_ms:6.2f} ms | Frame 1: {img_len_kb:5.1f} KB | FOV: {result['coordinates']['fov_arcmin']:.1f}'")

def test_difference_imaging_math():
    print_banner("3. ALARD-LUPTON DIFFERENCE IMAGING TEST")
    import numpy as np
    
    # Create synthetic test frames with stationary background and moving transient
    rng = np.random.default_rng(42)
    dim = 200
    epoch1 = rng.normal(100.0, 10.0, (dim, dim)).astype(np.float32)
    epoch2 = rng.normal(100.0, 10.0, (dim, dim)).astype(np.float32)

    # Add stationary star
    epoch1[95:105, 95:105] += 500.0
    epoch2[95:105, 95:105] += 500.0

    # Add moving star (proper motion dipole)
    epoch1[48:52, 48:52] += 600.0  # Epoch 1 position
    epoch2[58:62, 58:62] += 600.0  # Epoch 2 shifted position

    t0 = time.perf_counter()
    diff = compute_scientific_difference(epoch1, epoch2)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert diff.shape == (dim, dim)
    assert diff.dtype == np.uint8
    # Background should cluster around neutral mid-gray (128)
    median_val = float(np.median(diff))
    assert 120 <= median_val <= 136, f"Neutral mid-gray offset unexpected: {median_val}"
    
    print(f"  [PASS] Difference Map Computed in {elapsed_ms:.2f} ms")
    print(f"  [PASS] Background Median: {median_val:.1f} (Centered at neutral 128 mid-gray)")
    print(f"  [PASS] Dynamic Range: Min {np.min(diff)} (Negative Dipole) to Max {np.max(diff)} (Positive Dipole)")

def test_102_band_spectroscopy():
    print_banner("4. 102-BAND NEAR-INFRARED SPHEREx SPECTROSCOPY")
    for key in ["wise0855", "barnard"]:
        t0 = time.perf_counter()
        spec = get_102_band_spectrum(BENCHMARKS[key]["ra"], BENCHMARKS[key]["dec"], target_key=key)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Assertions
        assert "wavelengths_microns" in spec
        assert "flux_microjanskys" in spec
        assert len(spec["wavelengths_microns"]) == 102, f"Expected 102 bands, got {len(spec['wavelengths_microns'])}"
        assert len(spec["flux_microjanskys"]) == 102
        assert spec["wavelengths_microns"][0] == 0.75, f"Start band should be 0.75 μm, got {spec['wavelengths_microns'][0]}"
        assert spec["wavelengths_microns"][-1] == 5.0, f"End band should be 5.0 μm, got {spec['wavelengths_microns'][-1]}"
        assert "detected_molecules" in spec

        features = [f["molecule"] for f in spec["detected_molecules"]]
        print(f"  [PASS] {BENCHMARKS[key]['name']:<22} | 102 Bands Generated in {elapsed_ms:5.2f} ms | Detected: {', '.join(features)}")

def test_fastapi_endpoints():
    print_banner("5. FASTAPI ROUTE HANDLERS & ASTROPY COORDINATE PARSER")

    # 1. Health check
    h = health_check()
    assert h["status"] == "online"
    print(f"  [PASS] health_check()            -> Status: {h['status']}, Engine: {h['engine']}")

    # 2. Benchmark targets endpoint
    targets = get_benchmark_targets()
    assert len(targets) >= 5
    print(f"  [PASS] get_benchmark_targets()   -> Returned {len(targets)} verified benchmark targets")

    # 3. Astropy coordinate parser (decimal and sexagesimal)
    ra_dec, dec_deg = parse_celestial_coords("133.79513", "-7.24515")
    assert abs(ra_dec - 133.79513) < 1e-4
    assert abs(dec_deg - (-7.24515)) < 1e-4

    ra_sex, dec_sex = parse_celestial_coords("08h55m10.831s", "-07d14m42.53s")
    assert abs(ra_sex - 133.7951) < 0.01
    assert abs(dec_sex - (-7.2451)) < 0.01
    print(f"  [PASS] parse_celestial_coords()  -> Sexagesimal '08h55m10.831s -07d14m42.53s' parsed to ({ra_sex:.4f}°, {dec_sex:.4f}°)")

    # 4. FITS cutout endpoint
    cutout = get_cutout(ra="133.79513", dec="-7.24515", target="wise0855", fov=3.0, lod=1)
    assert cutout["status"] == "success"
    assert len(cutout["epochs"]) == 2
    print(f"  [PASS] get_cutout()              -> Target: {cutout['target']}, Archive: {cutout['archive_survey']}")

    # 5. 102-band spectrum endpoint
    spec = get_spectrum(ra="133.79513", dec="-7.24515", target="wise0855")
    assert len(spec["wavelengths_microns"]) == 102
    print(f"  [PASS] get_spectrum()            -> Target: WISE 0855, Channels: {len(spec['wavelengths_microns'])} (0.75 - 5.0 μm)")

    # 6. Citizen science discovery logger
    test_cand = DiscoveryCandidate(
        ra=133.79513,
        dec=-7.24515,
        object_type="High Proper Motion Brown Dwarf",
        user_handle="@darkodu",
        notes="Fast moving dipole verified in SPHEREx Hunter backend test suite",
        target_name="WISE 0855 Test Flag"
    )
    flag_res = flag_candidate(test_cand)
    assert flag_res["status"] == "recorded"
    discoveries = get_discoveries()
    assert len(discoveries) > 0
    print(f"  [PASS] flag_candidate()          -> Logged candidate by {test_cand.user_handle} (Total logged: {len(discoveries)})")

    # 7. Gaia DR3 catalog query
    gaia_res = get_gaia_catalog(ra="269.45208", dec="4.69339", radius=3.0, limit=10)
    assert gaia_res["status"] == "success"
    assert gaia_res["total_sources"] > 0
    top_star = gaia_res["sources"][0]
    assert "source_id" in top_star
    assert "pmra_mas_yr" in top_star
    assert "pmdec_mas_yr" in top_star
    print(f"  [PASS] get_gaia_catalog()        -> Retrieved {gaia_res['total_sources']} Gaia DR3 sources (Top star G={top_star['g_mag']}, PM={top_star['total_pm_mas_yr']:.1f} mas/yr)")

def test_gaia_catalog_direct():
    print_banner("6. GAIA DR3 ASTROMETRIC ENGINE & PROPER MOTION VECTORS")
    t0 = time.perf_counter()
    res = query_gaia_dr3(ra=269.45208, dec=4.69339, radius_arcmin=3.0, limit=20)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert res["status"] == "success"
    assert len(res["sources"]) > 0
    high_pm = [s for s in res["sources"] if s.get("is_high_proper_motion")]
    print(f"  [PASS] Gaia DR3 Catalog queried in {elapsed_ms:5.2f} ms")
    print(f"  [PASS] Total sources in 3.0' FOV: {res['total_sources']}, High Proper Motion: {len(high_pm)}")
    if high_pm:
        hero = high_pm[0]
        print(f"  [PASS] Hero High PM Object: PM_RA={hero['pmra_mas_yr']:.1f} mas/yr, PM_DEC={hero['pmdec_mas_yr']:.1f} mas/yr (Total: {hero['total_pm_mas_yr']:.1f} mas/yr)")
        if hero.get('distance_pc'):
            print(f"  [PASS] Parallax Distance: {hero['distance_pc']:.2f} pc ({hero['distance_pc']*3.26:.2f} light years)")

if __name__ == "__main__":
    print("\nStarting SPHEREx Hunter Astro-Data Backend Diagnostic Suite...")
    test_benchmark_targets()
    test_cutout_engine_lods()
    test_difference_imaging_math()
    test_102_band_spectroscopy()
    test_fastapi_endpoints()
    test_gaia_catalog_direct()
    print_banner("ALL DIAGNOSTIC TESTS PASSED! (6/6 SUITES 100% OPERATIONAL)")
