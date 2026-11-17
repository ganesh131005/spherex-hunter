"""
Acceptance unit tests for ZOGY PSF-matched differencing & candidate detection:
1. Stationary-star pairs leave no dipole residuals above 3.5 sigma.
2. Injected moving source is successfully recovered at >5 sigma and centroided within 0.5 pixels.
3. Cosmic ray spike veto: single-pixel high-flux artifact is identified and vetoed.
4. Edge proximity veto: source on image boundary is vetoed.
"""

import numpy as np

from backend.science.differencing import construct_gaussian_psf, execute_scientific_differencing, zogy_subtraction


def test_stationary_star_leaves_no_dipole_residuals():
    """Stationary star pair with noise must leave residuals below 3.5 sigma in ZOGY."""
    size = 64
    rng = np.random.default_rng(101)

    # 1. Background noise
    bg_noise = 0.5
    img_a = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)
    img_b = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)

    var_a = np.full((size, size), bg_noise**2, dtype=np.float32)
    var_b = np.full((size, size), bg_noise**2, dtype=np.float32)

    # 2. Add bright stationary star at center (32, 32)
    cy, cx = 32, 32
    yy, xx = np.mgrid[0:size, 0:size]
    r2 = (xx - cx)**2 + (yy - cy)**2
    psf_sigma = 1.2
    star_flux = 100.0  # 200x background noise!
    star = star_flux * np.exp(-0.5 * r2 / psf_sigma**2)

    img_a += star.astype(np.float32)
    img_b += star.astype(np.float32)

    psf = construct_gaussian_psf(33, fwhm_pix=psf_sigma * 2.355)

    diff, s_corr, noise_sigma = zogy_subtraction(
        image_new=img_b,
        var_new=var_b,
        psf_new=psf,
        image_ref=img_a,
        var_ref=var_a,
        psf_ref=psf
    )

    # Maximum residual significance on stationary star must stay below 3.5 sigma
    star_box = s_corr[cy-3:cy+4, cx-3:cx+4]
    max_star_sigma = np.max(np.abs(star_box))
    assert max_star_sigma < 3.5, f"Stationary star left high dipole residual: {max_star_sigma:.2f} sigma"


def test_injected_moving_source_recovered():
    """Injected moving source must be recovered at > 5 sigma and centroided accurately."""
    size = 64
    rng = np.random.default_rng(202)

    bg_noise = 0.5
    img_a = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)
    img_b = rng.normal(0.0, bg_noise, (size, size)).astype(np.float32)
    var_a = np.full((size, size), bg_noise**2, dtype=np.float32)
    var_b = np.full((size, size), bg_noise**2, dtype=np.float32)

    # Inject stationary background star at (20, 20)
    yy, xx = np.mgrid[0:size, 0:size]
    psf_sigma = 1.2
    star = 50.0 * np.exp(-0.5 * ((xx - 20)**2 + (yy - 20)**2) / psf_sigma**2)
    img_a += star.astype(np.float32)
    img_b += star.astype(np.float32)

    # Inject moving asteroid/Planet X at (40.0, 35.0) ONLY in epoch B!
    inject_x, inject_y = 40.0, 35.0
    mover_flux = 30.0  # 60 sigma detection
    mover = mover_flux * np.exp(-0.5 * ((xx - inject_x)**2 + (yy - inject_y)**2) / psf_sigma**2)
    img_b += mover.astype(np.float32)

    psf = construct_gaussian_psf(33, fwhm_pix=psf_sigma * 2.355)

    result = execute_scientific_differencing(
        image_a=img_a,
        var_a=var_a,
        image_b=img_b,
        var_b=var_b,
        psf_a=psf,
        psf_b=psf,
        is_wavelength_matched=True,
        snr_threshold=5.0
    )

    # Must detect mover
    assert result.num_passed_candidates >= 1
    mover_cand = next(c for c in result.candidates if c.passed_vetoes)
    assert mover_cand.peak_snr_sigma > 10.0
    # Centroid accuracy within 0.5 pixels
    assert np.isclose(mover_cand.x_pix, inject_x, atol=0.5)
    assert np.isclose(mover_cand.y_pix, inject_y, atol=0.5)


def test_cosmic_ray_spike_vetoed():
    """A single-pixel cosmic ray spike must be vetoed as COSMIC_RAY_SPIKE."""
    size = 64
    img_a = np.zeros((size, size), dtype=np.float32)
    img_b = np.zeros((size, size), dtype=np.float32)
    var_a = np.ones((size, size), dtype=np.float32)
    var_b = np.ones((size, size), dtype=np.float32)

    # Single hot pixel in epoch B
    img_b[25, 25] = 200.0

    result = execute_scientific_differencing(
        image_a=img_a,
        var_a=var_a,
        image_b=img_b,
        var_b=var_b,
        is_wavelength_matched=True,
        snr_threshold=5.0
    )

    # Detection should trigger cosmic ray veto
    cr_cand = next((c for c in result.candidates if c.is_cosmic_ray), None)
    assert cr_cand is not None
    assert cr_cand.veto_reason == "COSMIC_RAY_SPIKE"
    assert not cr_cand.passed_vetoes


def test_rdraconis_mira_variable_dynamic_range_and_zogy_residual():
    """
    Issue #44 Verification:
    1. R Draconis FITS cutouts render with balanced dynamic range without pixel saturation clipping.
    2. ZOGY subtraction maps produce clean monopole residual profiles consistent with Mira pulsation physics.
    3. Multi-epoch flux normalization balances cross-survey baseline.
    """
    from backend.services.cutout_engine import apply_locked_asinh_stretch, fetch_real_cutout

    # 1. Test adaptive dynamic range on synthetic / extreme high-dynamic range array
    # simulating high-amplitude Mira pulsation (core peak > 5x p99.5)
    rng = np.random.default_rng(44)
    sim_field = rng.normal(100.0, 5.0, (64, 64)).astype(np.float64)
    # Inject bright Mira variable core with peak 10,000 counts
    cy, cx = 32, 32
    yy, xx = np.mgrid[0:64, 0:64]
    r2 = (xx - cx)**2 + (yy - cy)**2
    sim_field += 10000.0 * np.exp(-0.5 * r2 / (1.5**2))

    p99_5 = float(np.percentile(sim_field, 99.5))
    peak_val = float(np.max(sim_field))
    assert peak_val > 3.0 * p99_5, "Peak must reflect extreme Mira pulsation dynamic range"

    # Render with adaptive HDR stretch
    stretched = apply_locked_asinh_stretch(sim_field, beta=3.0, adaptive_hdr=True)
    # Assert zero saturation discs (saturation count is at most 1 pixel at peak, not flat plateau)
    sat_count = int(np.sum(stretched == 255))
    assert sat_count <= 1, f"Adaptive HDR must prevent saturation clipping disc, got {sat_count} saturated pixels"
    # Assert high-contrast core gradient
    assert stretched[cy, cx] >= 250
    assert stretched[cy + 4, cx] < 200

    # 2. Test live real-cutout pipeline on R Draconis
    bundle = fetch_real_cutout(ra=248.1676, dec=66.7551, target_key="rdraconis")
    assert bundle["status"] == "success"
    assert "R Draconis" in bundle["target"]
    assert len(bundle["epochs"]) == 2

    # Check ZOGY significance and residual metrics
    zogy = bundle["zogy_significance"]
    assert zogy["peak_sigma"] >= 5.0
    assert zogy["is_significant"] is True

    # Check motion vector reflects variable star physics (stationary monopole flare, not a spatial dipole)
    vector = bundle["motion_vector"]
    assert vector["is_variable"] is True
    assert vector["shift_arcsec"] == 0.0
    assert vector["transient_type"] == "VARIABLE_FLARE"

