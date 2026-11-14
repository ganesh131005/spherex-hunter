"""
NASA Space Apps Challenge 2026 - Golden Verification Suite
Validates the 5 NASA Benchmark Targets, WCS Astrometry, Difference Imaging,
and 102-Band Infrared Spectrophotometry against the Spec-Kit requirements.
"""
import pytest
from astropy.coordinates import SkyCoord

from backend.services.cutout_engine import fetch_real_cutout, get_102_band_spectrum

BENCHMARKS = [
    ("wise0855", 133.79513, -7.24515, "WISE 0855-0714"),
    ("barnard", 269.4521, 4.6934, "Barnard's Star"),
    ("epsindi", 331.0438, -56.7827, "Epsilon Indi B"),
    ("rwaur", 76.9564, 30.4014, "RW Aurigae"),
    ("rdraconis", 248.1676, 66.7551, "R Draconis"),
]

@pytest.mark.parametrize("target_key,ra,dec,expected_name", BENCHMARKS)
def test_nasa_benchmark_cutouts(target_key, ra, dec, expected_name):
    bundle = fetch_real_cutout(ra=ra, dec=dec, target_key=target_key)
    assert bundle["status"] == "success"
    assert expected_name in bundle["target"]
    assert len(bundle["epochs"]) == 2
    assert "image_data" in bundle["difference_image"]
    assert len(bundle["difference_image"]["image_data"]) > 100

def test_sexagesimal_and_decimal_parsing():
    # Decimal
    bundle_dec = fetch_real_cutout(ra=133.79513, dec=-7.24515)
    assert bundle_dec["status"] == "success"
    assert abs(bundle_dec["coordinates"]["ra_deg"] - 133.79513) < 0.001

    # Sexagesimal parse via Astropy
    coord = SkyCoord("08h55m10.831s", "-07d14m42.53s", frame="icrs")
    bundle_sex = fetch_real_cutout(ra=coord.ra.deg, dec=coord.dec.deg)
    assert bundle_sex["status"] == "success"
    assert abs(bundle_sex["coordinates"]["ra_deg"] - 133.79513) < 0.001

def test_102_band_spectroscopy():
    spec = get_102_band_spectrum(133.79513, -7.24515, "wise0855")
    assert len(spec["wavelengths_microns"]) == 102
    assert len(spec["flux_microjanskys"]) == 102
    assert len(spec["detector_arrays"]) == 6
    assert len(spec["detected_molecules"]) >= 3
    # Verify range 0.75 um to 5.00 um
    assert spec["wavelengths_microns"][0] == 0.75
    assert spec["wavelengths_microns"][-1] == 5.00

def test_gaia_dr3_astrometry():
    from backend.services.gaia_service import query_gaia_dr3
    res = query_gaia_dr3(269.45208, 4.69339, radius_arcmin=3.0)
    assert res["status"] == "success"
    assert res["catalog"] == "Gaia Data Release 3 (Gaia DR3)"
    assert res["matched_count"] > 0
    # Barnard's Star is the brightest/fastest source with PM > 10,000 mas/yr
    fast_stars = [s for s in res["sources"] if s["total_pm_mas_yr"] and s["total_pm_mas_yr"] > 10000.0]
    assert len(fast_stars) >= 1
    assert abs(fast_stars[0]["total_pm_mas_yr"] - 10393.3) < 20.0
