"""
color_transfer.py — Reinhard LAB color transfer algorithm.

Allows the user to recolor a hair overlay to match a chosen target color.

Pipeline:
  1. Isolate opaque pixels of the hair overlay (alpha > threshold)
  2. Convert those pixels to L*a*b* color space
  3. Scale mean + standard deviation of a* and b* channels
     to match the target color
  4. Convert back to RGBA
"""

import numpy as np
from typing import Tuple
from utils.math_utils import rgb_to_lab, lab_to_rgb, clamp_array


# ---------------------------------------------------------------------------
# Color transfer
# ---------------------------------------------------------------------------

def transfer_hair_color(overlay: np.ndarray,
                        target_rgb: Tuple[int, int, int],
                        strength: float = 1.0) -> np.ndarray:
    """
    Recolor the hair in `overlay` to match `target_rgb`.

    Parameters
    ----------
    overlay    : (H, W, 4) RGBA uint8 — the hairstyle overlay
    target_rgb : (R, G, B) tuple, 0-255 — desired hair color
    strength   : blending strength 0.0 (no change) – 1.0 (full transfer)

    Returns
    -------
    (H, W, 4) RGBA uint8 with recolored hair
    """
    result = overlay.copy()
    alpha = overlay[:, :, 3]

    # Only touch pixels that are at least 10% opaque
    mask = alpha > 25  # bool (H, W)
    if not mask.any():
        return result

    # Extract opaque hair pixels (H_m, 3) uint8
    hair_rgb = overlay[:, :, :3][mask]  # (N, 3)

    # Convert to L*a*b*
    hair_lab = rgb_to_lab(hair_rgb[None, :, :])  # (1, N, 3)
    hair_lab = hair_lab[0]  # (N, 3)

    # Build a 1-pixel "target" in LAB
    target_arr = np.array([[target_rgb]], dtype=np.uint8)  # (1, 1, 3)
    target_lab = rgb_to_lab(target_arr)[0, 0]  # (3,)

    # Reinhard transfer on a* and b* channels
    src_mean_a, src_std_a = hair_lab[:, 1].mean(), hair_lab[:, 1].std() + 1e-6
    src_mean_b, src_std_b = hair_lab[:, 2].mean(), hair_lab[:, 2].std() + 1e-6

    # Target std estimated from a small Gaussian around target_lab
    tgt_std_a = max(src_std_a * 0.8, 5.0)
    tgt_std_b = max(src_std_b * 0.8, 5.0)

    new_a = (hair_lab[:, 1] - src_mean_a) * (tgt_std_a / src_std_a) + target_lab[1]
    new_b = (hair_lab[:, 2] - src_mean_b) * (tgt_std_b / src_std_b) + target_lab[2]

    # Preserve luminance (L), only shift chrominance
    out_lab = hair_lab.copy()
    out_lab[:, 1] = new_a
    out_lab[:, 2] = new_b

    # Blend with original based on strength
    out_lab = hair_lab + strength * (out_lab - hair_lab)

    # Convert back to RGB
    out_rgb = lab_to_rgb(out_lab[None, :, :])[0]  # (N, 3)

    # Write back into result
    result_rgb = result[:, :, :3].copy()
    result_rgb[mask] = out_rgb
    result[:, :, :3] = result_rgb
    return result


# ---------------------------------------------------------------------------
# Brightness / contrast adjustments
# ---------------------------------------------------------------------------

def adjust_brightness(overlay: np.ndarray, factor: float) -> np.ndarray:
    """
    Scale RGB channels of opaque overlay pixels by `factor`.
    factor > 1 → brighter, factor < 1 → darker.
    """
    result = overlay.copy()
    mask = overlay[:, :, 3] > 25
    rgb = result[:, :, :3].astype(np.float64)
    rgb[mask] = clamp_array(rgb[mask] * factor, 0, 255)
    result[:, :, :3] = rgb.astype(np.uint8)
    return result


def adjust_opacity(overlay: np.ndarray, opacity: float) -> np.ndarray:
    """
    Scale the alpha channel of the overlay uniformly.
    opacity ∈ [0.0, 1.0].
    """
    result = overlay.copy()
    result[:, :, 3] = (result[:, :, 3].astype(np.float64) * opacity).astype(np.uint8)
    return result


# ---------------------------------------------------------------------------
# Convenience: parse hex color string
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert '#RRGGBB' or 'RRGGBB' to (R, G, B)."""
    h = hex_color.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
