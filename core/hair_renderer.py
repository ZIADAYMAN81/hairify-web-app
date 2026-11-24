"""
hair_renderer.py — Composites a hairstyle overlay onto a photo.

Steps:
  1. Scale + translate the overlay to match landmark positions
     (warp_affine with bilinear interpolation — from scratch)
  2. Feather the edges with a Gaussian blur on the alpha channel
  3. Alpha-composite overlay onto the base photo
  4. Optionally add a soft root shadow
"""

import numpy as np
from typing import Tuple, Optional

from utils.math_utils import (
    gaussian_blur, make_scale_translate_matrix, warp_affine, clamp_array
)
from core.landmark_finder import LandmarkResult


# ---------------------------------------------------------------------------
# Main rendering function
# ---------------------------------------------------------------------------

def render_hair(base: np.ndarray,
                overlay: np.ndarray,
                landmarks: LandmarkResult,
                offset_x: float = 0.0,
                offset_y: float = 0.0,
                scale: float = 1.0,
                feather_sigma: float = 2.0,
                shadow: bool = True) -> np.ndarray:
    """
    Composite a hairstyle overlay onto a base photo.

    Parameters
    ----------
    base        : (H, W, 4) RGBA uint8 — the user's photo
    overlay     : (H, W, 4) RGBA uint8 — the hairstyle (procedurally generated)
    landmarks   : LandmarkResult from landmark_finder
    offset_x/y  : manual pixel nudge (for drag-to-reposition)
    scale       : additional scale factor applied on top of auto-fit
    feather_sigma: Gaussian sigma for edge softening
    shadow      : whether to add a root shadow ellipse

    Returns
    -------
    (H, W, 4) RGBA uint8 composited image
    """
    img_h, img_w = base.shape[:2]

    # ---- 1. Determine target overlay position & size ----
    ov_x = landmarks.overlay_x + offset_x
    ov_y = landmarks.overlay_y + offset_y
    ov_w = landmarks.overlay_w * scale
    ov_h = landmarks.overlay_h * scale

    # Clamp to image bounds (allow partial overlap)
    ov_w = min(ov_w, img_w * 1.5)
    ov_h = min(ov_h, img_h * 1.2)

    # ---- 2. Warp overlay to target position ----
    src_h, src_w = overlay.shape[:2]
    if src_w == 0 or src_h == 0:
        return base.copy()

    sx = ov_w / src_w
    sy = ov_h / src_h
    tx = ov_x
    ty = ov_y

    M = make_scale_translate_matrix(sx, sy, tx, ty)
    warped_f = warp_affine(overlay.astype(np.float64), M, (img_w, img_h))
    warped = np.clip(warped_f, 0, 255).astype(np.uint8)

    # ---- 3. Feather alpha channel ----
    alpha_f = warped[:, :, 3:4].astype(np.float64)
    alpha_blurred = gaussian_blur(alpha_f, sigma=feather_sigma, radius=int(feather_sigma * 2))
    warped[:, :, 3] = np.clip(alpha_blurred[:, :, 0], 0, 255).astype(np.uint8)

    # ---- 4. Optional root shadow ----
    if shadow:
        warped = _add_root_shadow(warped, landmarks, offset_x, offset_y, img_w, img_h)

    # ---- 5. Alpha composite ----
    result = alpha_composite(base, warped)
    return result


# ---------------------------------------------------------------------------
# Alpha compositing (from scratch)
# ---------------------------------------------------------------------------

def alpha_composite(dst: np.ndarray, src: np.ndarray) -> np.ndarray:
    """
    Porter-Duff "over" composite: place src over dst.

    Both arrays must be (H, W, 4) RGBA uint8 with the same shape.
    Returns (H, W, 4) RGBA uint8.
    """
    assert dst.shape == src.shape, "dst and src must have the same shape"

    src_a = src[:, :, 3:4].astype(np.float64) / 255.0  # (H, W, 1)
    dst_a = dst[:, :, 3:4].astype(np.float64) / 255.0

    src_rgb = src[:, :, :3].astype(np.float64)
    dst_rgb = dst[:, :, :3].astype(np.float64)

    # out_rgb = src_rgb * src_a + dst_rgb * dst_a * (1 - src_a)
    out_a = src_a + dst_a * (1.0 - src_a)
    # Avoid divide-by-zero where out_a == 0
    safe_a = np.where(out_a > 0, out_a, 1.0)
    out_rgb = (src_rgb * src_a + dst_rgb * dst_a * (1.0 - src_a)) / safe_a

    out = np.zeros_like(dst)
    out[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
    out[:, :, 3]  = np.clip(out_a[:, :, 0] * 255.0, 0, 255).astype(np.uint8)
    return out


# ---------------------------------------------------------------------------
# Root shadow
# ---------------------------------------------------------------------------

def _add_root_shadow(warped: np.ndarray,
                     landmarks: LandmarkResult,
                     offset_x: float, offset_y: float,
                     img_w: int, img_h: int) -> np.ndarray:
    """
    Add a soft elliptical shadow at the hairline root to improve realism.
    """
    result = warped.copy().astype(np.float64)
    cx = int(landmarks.face_cx + offset_x)
    root_y = int(landmarks.overlay_y + landmarks.overlay_h * 0.42 + offset_y)
    rx = int(landmarks.face_width * 0.4)
    ry = int(landmarks.face_height * 0.04)

    shadow_layer = np.zeros((img_h, img_w, 4), dtype=np.float64)
    # Draw a filled ellipse with partial opacity
    y0 = max(0, root_y - ry * 2)
    y1 = min(img_h, root_y + ry * 2)
    for y in range(y0, y1):
        dy = y - root_y
        if ry == 0:
            continue
        frac = 1.0 - (dy / (ry * 2)) ** 2
        if frac <= 0:
            continue
        hw = int(rx * (frac ** 0.5))
        xs = max(0, cx - hw)
        xe = min(img_w, cx + hw)
        shadow_layer[y, xs:xe, 3] = frac * 55.0  # semi-transparent dark

    # Blur the shadow
    shadow_blurred = gaussian_blur(shadow_layer, sigma=4.0, radius=8)
    # Add shadow behind hair (only where hair has alpha)
    hair_alpha = warped[:, :, 3:4].astype(np.float64) / 255.0
    extra_alpha = shadow_blurred[:, :, 3:4] * hair_alpha
    result[:, :, 3] = np.clip(result[:, :, 3] + extra_alpha[:, :, 0], 0, 255)
    return result.astype(np.uint8)


# ---------------------------------------------------------------------------
# Utility: create a split-view (before|after) image
# ---------------------------------------------------------------------------

def make_split_view(base: np.ndarray, composited: np.ndarray,
                    split_ratio: float = 0.5) -> np.ndarray:
    """
    Return a side-by-side before/after view.

    split_ratio: where the vertical divider sits (0.5 = centre).
    """
    H, W = base.shape[:2]
    split_x = int(W * split_ratio)
    result = composited.copy()
    result[:, :split_x] = base[:, :split_x]
    # Draw divider line
    lw = 2
    result[:, max(0, split_x - lw):split_x + lw] = [255, 255, 255, 200]
    return result
