"""
🌌 SPHEREx Hunter - Image Math, Difference Engine & AI
NASA Space Apps Challenge 2026 - Planet X & SPHEREx
Lead: iceodu
"""

from .coaddition import (
    SPHEREX_DETECTOR_ARRAYS,
    build_spherex_6array_broadbands,
    coadd_channels,
    coadd_real_fits_multiband,
)
from .difference import (
    calculate_cancellation_residual_rms,
    compute_difference_image,
    process_real_fits_difference,
    render_difference_base64,
    save_difference_png,
)

__all__ = [
    "compute_difference_image",
    "process_real_fits_difference",
    "save_difference_png",
    "render_difference_base64",
    "calculate_cancellation_residual_rms",
    "coadd_channels",
    "build_spherex_6array_broadbands",
    "coadd_real_fits_multiband",
    "SPHEREX_DETECTOR_ARRAYS"
]
