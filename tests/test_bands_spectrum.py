"""
🛰️ SPHEREx Hunter - 102-Band Spectroscopy & Structural Metadata Tests
Validates GitHub Issue #7: 6-Array Selector, 17-Wavelength Stepper & SED Visualizer
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_bands_endpoint_structural_metadata():
    """Validates that GET /api/bands returns 102 channels across 6 arrays (A1-A6)."""
    resp = client.get("/api/bands")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["total_bands"] == 102
    assert len(data["arrays"]) == 6
    assert len(data["bands"]) == 102

    array_ids = [a["array_id"] for a in data["arrays"]]
    assert array_ids == ["A1", "A2", "A3", "A4", "A5", "A6"]

    # Verify first and last channel wavelengths
    assert data["bands"][0]["band_id"] == 1
    assert data["bands"][0]["array_id"] == "A1"
    assert data["bands"][0]["wavelength_um"] == 0.750

    assert data["bands"][-1]["band_id"] == 102
    assert data["bands"][-1]["array_id"] == "A6"
    assert data["bands"][-1]["wavelength_um"] == 5.000

    # Verify molecular flags present
    flagged = [b for b in data["bands"] if b.get("molecular_flag")]
    assert len(flagged) >= 4
    flags = {b["molecular_flag"] for b in flagged}
    assert "H2O" in flags
    assert "CH4" in flags
    assert "CO2_ICE" in flags
    assert "CO" in flags

def test_spectrum_endpoint_with_bands_and_summary():
    """Validates that GET /api/spectrum returns 102 bands and A1-A6 array_summary."""
    resp = client.get("/api/spectrum?ra=133.79513&dec=-7.24515&target=wise0855")
    assert resp.status_code == 200
    data = resp.json()

    assert data["available"] is True
    assert len(data["bands"]) == 102
    assert "array_summary" in data

    summary = data["array_summary"]
    for arr_id in ["A1", "A2", "A3", "A4", "A5", "A6"]:
        assert arr_id in summary
        assert "avg_flux_ujy" in summary[arr_id]
        assert "total_counts" in summary[arr_id]
        assert "band_range" in summary[arr_id]

    # Verify individual band schema
    first_band = data["bands"][0]
    assert first_band["band_id"] == 1
    assert first_band["array_id"] == "A1"
    assert "flux_ujy" in first_band
    assert "wavelength_um" in first_band
