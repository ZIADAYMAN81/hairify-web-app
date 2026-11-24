"""
image_utils.py — Image I/O and basic array helpers.

Uses Pillow only for reading/writing files and for converting
to/from NumPy arrays.  All processing logic lives in other modules.
"""

import os
import numpy as np
from PIL import Image
from typing import Tuple, Optional


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------

def load_image(path: str) -> np.ndarray:
    """
    Load an image file as a (H, W, 4) RGBA uint8 NumPy array.
    Supports PNG, JPEG, BMP, TIFF, WEBP.
    """
    img = Image.open(path).convert("RGBA")
    return np.array(img, dtype=np.uint8)


def save_image(arr: np.ndarray, path: str) -> None:
    """
    Save a (H, W, 4) RGBA uint8 NumPy array to disk.
    Format is inferred from the file extension.
    """
    if arr.shape[2] == 4 and path.lower().endswith(('.jpg', '.jpeg')):
        # JPEG does not support alpha — flatten onto white
        arr = alpha_composite_on_white(arr)
    img = Image.fromarray(arr)
    img.save(path)


def array_to_pil(arr: np.ndarray) -> Image.Image:
    """Convert a (H, W, 4) RGBA uint8 array to a Pillow Image."""
    return Image.fromarray(arr.astype(np.uint8), mode="RGBA")


def pil_to_array(img: Image.Image) -> np.ndarray:
    """Convert a Pillow Image to a (H, W, 4) RGBA uint8 NumPy array."""
    return np.array(img.convert("RGBA"), dtype=np.uint8)


def resize_array(arr: np.ndarray, new_w: int, new_h: int) -> np.ndarray:
    """
    Resize a (H, W, C) uint8 array using Pillow (nearest/bilinear).
    Keeps aspect ratio correction responsibility with the caller.
    """
    img = Image.fromarray(arr.astype(np.uint8))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    return np.array(img, dtype=np.uint8)


# ---------------------------------------------------------------------------
# RGBA helpers
# ---------------------------------------------------------------------------

def ensure_rgba(arr: np.ndarray) -> np.ndarray:
    """Convert (H, W, 3) RGB or (H, W, 4) RGBA array to (H, W, 4) RGBA."""
    if arr.ndim == 2:
        # Greyscale → RGBA
        rgb = np.stack([arr, arr, arr], axis=-1)
        alpha = np.full(arr.shape, 255, dtype=np.uint8)
        return np.concatenate([rgb, alpha[:, :, None]], axis=-1)
    if arr.shape[2] == 3:
        alpha = np.full((arr.shape[0], arr.shape[1], 1), 255, dtype=np.uint8)
        return np.concatenate([arr, alpha], axis=-1)
    return arr.copy()


def split_rgba(arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return (rgb, alpha) where rgb is (H,W,3) and alpha is (H,W) float64 0-1."""
    rgba = ensure_rgba(arr)
    rgb = rgba[:, :, :3].astype(np.float64)
    alpha = rgba[:, :, 3].astype(np.float64) / 255.0
    return rgb, alpha


def alpha_composite_on_white(arr: np.ndarray) -> np.ndarray:
    """Flatten RGBA onto a white background.  Returns (H, W, 3) uint8."""
    rgb, alpha = split_rgba(arr)
    white = np.ones_like(rgb) * 255.0
    out = rgb * alpha[:, :, None] + white * (1 - alpha[:, :, None])
    return np.clip(out, 0, 255).astype(np.uint8)


def new_canvas(width: int, height: int,
               color: Tuple = (0, 0, 0, 0)) -> np.ndarray:
    """Create a blank (H, W, 4) RGBA canvas filled with `color`."""
    canvas = np.zeros((height, width, 4), dtype=np.uint8)
    canvas[:, :] = color
    return canvas


# ---------------------------------------------------------------------------
# Crop / pad
# ---------------------------------------------------------------------------

def crop(arr: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """Return a crop of arr starting at (x, y) with size (w, h)."""
    H, W = arr.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    return arr[y0:y1, x0:x1].copy()


def pad_to_size(arr: np.ndarray, target_w: int, target_h: int,
                fill: Tuple = (0, 0, 0, 0)) -> np.ndarray:
    """Pad arr with `fill` so its size becomes at least (target_w, target_h)."""
    H, W, C = arr.shape
    pad_h = max(0, target_h - H)
    pad_w = max(0, target_w - W)
    if pad_h == 0 and pad_w == 0:
        return arr
    result = np.full((H + pad_h, W + pad_w, C), fill, dtype=np.uint8)
    result[:H, :W] = arr
    return result


# ---------------------------------------------------------------------------
# Thumbnail helper for the gallery panel
# ---------------------------------------------------------------------------

def make_thumbnail(arr: np.ndarray,
                   size: Tuple[int, int] = (120, 120)) -> np.ndarray:
    """Return a square-cropped, resized thumbnail (H=size[1], W=size[0])."""
    tw, th = size
    H, W = arr.shape[:2]
    # Square-crop from centre
    if W > H:
        offset = (W - H) // 2
        arr = arr[:, offset:offset + H]
    elif H > W:
        offset = (H - W) // 2
        arr = arr[offset:offset + W, :]
    return resize_array(arr, tw, th)


# ---------------------------------------------------------------------------
# Image info
# ---------------------------------------------------------------------------

def image_size(arr: np.ndarray) -> Tuple[int, int]:
    """Return (width, height) of an image array."""
    return arr.shape[1], arr.shape[0]
