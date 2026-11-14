"""
🛰️ SPHEREx Hunter - Rigorous False-Positive Rate (FPR) Benchmark on Real Sky Data
NASA Space Apps Challenge 2026 - Team RIP

Sanity-Audited False-Positive Measurement:
1. Image Pair Used:
   - Exposure 1 (Reference): level2_2025W17_4B_0001_1D1_spx_l2b-v27-2026-196.fits (MJD 60789.750762)
   - Exposure 2 (New):       level2_2025W17_4B_0001_2D1_spx_l2b-v27-2026-196.fits (MJD 60789.752254)
   - Detector: 1 (D1), Filter: LVF Band 1 (0.7455 - 1.1167 um), Cadence: Δt = 128.9s.
2. Evaluated Field Area:
   - 1024x1024 pixel subfield, 931,033 valid overlapping pixels = 2.7219 deg^2.
3. Rates and Statistical Confidence:
   - Computes empirical rate per deg^2 with exact Poisson 95% confidence intervals.
   - Saves thumbnail collage of top false-alarm categories (dipoles, CR spikes, boundary steps).
"""

import csv
import os

import matplotlib
import numpy as np
from scipy import stats
from scipy.ndimage import map_coordinates

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits

from backend.science.differencing import construct_gaussian_psf, detect_and_veto_candidates, zogy_subtraction
from backend.science.preprocessing import compute_pixel_solid_angle_sr, preprocess_spherex_hdu

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_samples")
FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "figures")
FITS_1_PATH = os.path.join(DATA_DIR, "spherex_level2_sample.fits")
FITS_2_PATH = os.path.join(DATA_DIR, "spherex_level2_pair_epoch2.fits")
CSV_PATH = os.path.join(os.path.dirname(__file__), "false_positive_rates.csv")
os.makedirs(FIG_DIR, exist_ok=True)


def poisson_interval(k: int, confidence: float = 0.95) -> tuple[float, float]:
    """Computes exact Poisson confidence interval for count k."""
    alpha = 1.0 - confidence
    low = 0.5 * stats.chi2.ppf(alpha / 2.0, 2 * k) if k > 0 else 0.0
    high = 0.5 * stats.chi2.ppf(1.0 - alpha / 2.0, 2 * (k + 1))
    return float(low), float(high)


def run_false_positive_audit():
    print("🔬 Loading authentic SPHEREx Level 2 consecutive pair for FPR benchmark...")
    with fits.open(FITS_1_PATH) as h1, fits.open(FITS_2_PATH) as h2:
        prep1 = preprocess_spherex_hdu(h1)
        prep2 = preprocess_spherex_hdu(h2)

    w1 = prep1.wcs
    w2 = prep2.wcs

    cy, cx = 1020, 1020
    size = 1024
    y0, y1 = cy - size // 2, cy + size // 2
    x0, x1 = cx - size // 2, cx + size // 2

    patch1_flux = prep1.flux_ujy[y0:y1, x0:x1].copy()
    patch1_var = prep1.variance_ujy2[y0:y1, x0:x1].copy()

    yy, xx = np.mgrid[y0:y1, x0:x1]
    sky_coords = w1.pixel_to_world(xx, yy)
    x2_grid, y2_grid = w2.world_to_pixel(sky_coords)

    patch2_flux = map_coordinates(prep2.flux_ujy, [y2_grid, x2_grid], order=1, cval=np.nan).astype(np.float32)
    patch2_var = map_coordinates(prep2.variance_ujy2, [y2_grid, x2_grid], order=1, cval=np.nan).astype(np.float32)

    valid = np.isfinite(patch1_flux) & np.isfinite(patch2_flux) & (patch1_var > 0) & (patch2_var > 0)
    scale_arcsec, _ = compute_pixel_solid_angle_sr(w1)
    field_area_deg2 = np.sum(valid) * (scale_arcsec / 3600.0)**2
    print(f"📐 Analyzed overlapping real area: {field_area_deg2:.4f} deg^2 ({np.sum(valid)} pixels)")

    # Replace NaNs with median for Fourier transforms
    patch1_flux[~np.isfinite(patch1_flux)] = np.nanmedian(patch1_flux)
    patch2_flux[~np.isfinite(patch2_flux)] = np.nanmedian(patch2_flux)
    patch1_var[~np.isfinite(patch1_var)] = np.nanmedian(patch1_var)
    patch2_var[~np.isfinite(patch2_var)] = np.nanmedian(patch2_var)

    psf = construct_gaussian_psf(33, fwhm_pix=2.0)
    diff, s_corr, _ = zogy_subtraction(
        image_new=patch2_flux,
        var_new=patch2_var,
        psf_new=psf,
        image_ref=patch1_flux,
        var_ref=patch1_var,
        psf_ref=psf
    )

    thresholds = [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]
    records = []
    rates_raw = []
    rates_clean = []
    rates_clean_low = []
    rates_clean_high = []

    for thresh in thresholds:
        _, n_raw = detect_and_veto_candidates(diff, s_corr, snr_threshold=thresh, edge_margin_pix=0)
        cands_vetoed, _ = detect_and_veto_candidates(diff, s_corr, snr_threshold=thresh, edge_margin_pix=8)
        clean_cands = [c for c in cands_vetoed if c.passed_vetoes]
        n_clean = len(clean_cands)

        r_raw = n_raw / field_area_deg2
        r_clean = n_clean / field_area_deg2

        k_low, k_high = poisson_interval(n_clean, confidence=0.95)
        rate_low = k_low / field_area_deg2
        rate_high = k_high / field_area_deg2

        rates_raw.append(r_raw)
        rates_clean.append(r_clean)
        rates_clean_low.append(rate_low)
        rates_clean_high.append(rate_high)

        rejection_pct = ((n_raw - n_clean) / max(1, n_raw)) * 100.0

        records.append({
            "threshold_sigma": thresh,
            "raw_count": n_raw,
            "raw_rate_per_deg2": round(r_raw, 2),
            "clean_count": n_clean,
            "clean_rate_per_deg2": round(r_clean, 2),
            "clean_ci95_low": round(rate_low, 2),
            "clean_ci95_high": round(rate_high, 2),
            "veto_rejection_pct": round(rejection_pct, 1)
        })
        print(f"Thresh {thresh:.1f}σ: Raw={n_raw:4d} ({r_raw:6.1f}/deg²), Clean={n_clean:3d} ({r_clean:5.2f}/deg²), 95% CI: [{rate_low:.2f}, {rate_high:.2f}]/deg²")

    # Save to CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"💾 Saved false-positive rates to {CSV_PATH}")

    # Plot False-Positive Rate vs Threshold
    plt.figure(figsize=(8, 5.5), dpi=200)
    plt.plot(thresholds, rates_raw, "o--", color="#f44336", label="Raw Thresholding (Vetoes OFF)")
    err_low = [c - l for c, l in zip(rates_clean, rates_clean_low)]
    err_high = [h - c for c, h in zip(rates_clean, rates_clean_high)]
    plt.errorbar(
        thresholds, rates_clean, yerr=[err_low, err_high], fmt="s-", color="#4caf50",
        ecolor="#81c784", elinewidth=2, capsize=4, capthick=1.5,
        label="Clean Candidates (Vetoes ON, Poisson 95% CI)"
    )
    plt.axvline(5.0, color="#ff9800", linestyle=":", label="Production Detection Threshold (5.0σ)")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle=":", alpha=0.5)
    plt.xlabel("Significance Threshold S_corr (σ)", fontsize=11, fontweight="bold")
    plt.ylabel("False Alarms per Square Degree (deg⁻²)", fontsize=11, fontweight="bold")
    plt.title("SPHEREx Hunter - Empirical False-Positive Rate vs Significance\n(Pair: 2025W17_4B_0001_1D1 vs 2D1, Overlap: 2.72 deg², Δt = 129s)", fontsize=10)
    plt.legend(loc="upper right", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "false_positive_rate.png"))
    plt.close()
    print("📊 Generated corrected docs/figures/false_positive_rate.png")

    # Generate Thumbnails of Top Detections
    cands_all, _ = detect_and_veto_candidates(diff, s_corr, snr_threshold=5.0, edge_margin_pix=4)
    # Sort by peak SNR descending
    cands_sorted = sorted(cands_all, key=lambda c: c.peak_snr_sigma, reverse=True)

    fig, axes = plt.subplots(2, 3, figsize=(10, 6.5), dpi=200)
    fig.suptitle("SPHEREx Hunter - Real Flight Data Top Residuals & False Alarms\n(Difference Image D = I₂ - I₁ at 5.0σ, Real Level 2 Pair)", fontsize=11, fontweight="bold")

    thumb_examples = cands_sorted[:6]
    for i, ax in enumerate(axes.flat):
        if i < len(thumb_examples):
            cand = thumb_examples[i]
            cx_pix, cy_pix = int(round(cand.x_pix)), int(round(cand.y_pix))
            rad = 10
            y_m = max(0, cy_pix - rad)
            y_p = min(size, cy_pix + rad + 1)
            x_m = max(0, cx_pix - rad)
            x_p = min(size, cx_pix + rad + 1)
            cut = diff[y_m:y_p, x_m:x_p]

            ax.imshow(cut, cmap="RdBu_r", origin="lower", vmin=-50, vmax=50)
            status_color = "#4caf50" if cand.passed_vetoes else "#f44336"
            label_text = "PASSED" if cand.passed_vetoes else f"VETOED:\n{cand.veto_reason}"
            ax.set_title(f"Peak: {cand.peak_snr_sigma:.1f}σ\n{label_text}", fontsize=8, color=status_color)
            ax.axis("off")
        else:
            ax.axis("off")

    plt.tight_layout()
    thumb_path = os.path.join(FIG_DIR, "false_positive_thumbnails.png")
    plt.savefig(thumb_path)
    plt.close()
    print(f"🖼️ Generated thumbnail collage at {thumb_path}")


if __name__ == "__main__":
    run_false_positive_audit()
