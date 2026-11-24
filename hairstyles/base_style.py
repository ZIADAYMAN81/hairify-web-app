"""
base_style.py — Abstract base class for all hairstyles.

Each hairstyle subclass must implement:
  - generate_overlay(width, height) → (H, W, 4) RGBA uint8 NumPy array
  - A set of metadata class attributes
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple


class HairstyleBase(ABC):
    """Abstract base for all procedurally-generated hairstyle overlays."""

    # ---- Metadata (override in subclasses) ----
    name: str = "Unnamed"
    description: str = ""
    gender: str = "unisex"          # 'male', 'female', 'unisex'
    length: str = "medium"          # 'short', 'medium', 'long'
    # Default hair color (R, G, B)
    default_color: Tuple[int, int, int] = (60, 30, 10)
    # Thumbnail background color for the gallery (dark palette)
    thumb_bg: Tuple[int, int, int] = (30, 20, 40)

    # ---- Abstract interface ----

    @abstractmethod
    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        """
        Procedurally generate a hairstyle overlay.

        Parameters
        ----------
        width, height : canvas dimensions in pixels

        Returns
        -------
        (height, width, 4) RGBA uint8 array where the hair pixels have
        non-zero alpha and the transparent background has alpha = 0.
        """
        ...

    # ---- Shared helpers ----

    @staticmethod
    def blank(width: int, height: int) -> np.ndarray:
        """Return a blank (height, width, 4) RGBA uint8 canvas."""
        return np.zeros((height, width, 4), dtype=np.uint8)

    @staticmethod
    def set_pixels(canvas: np.ndarray,
                   mask: np.ndarray,
                   color: Tuple[int, int, int],
                   alpha: int = 255) -> None:
        """Write color + alpha to all True positions in mask."""
        canvas[mask, 0] = color[0]
        canvas[mask, 1] = color[1]
        canvas[mask, 2] = color[2]
        canvas[mask, 3] = alpha

    def thumbnail(self, size: int = 120) -> np.ndarray:
        """Return a small square thumbnail for the gallery panel."""
        ov = self.generate_overlay(size, size)
        # Composite on a dark background
        bg = np.zeros((size, size, 4), dtype=np.uint8)
        bg[:] = (*self.thumb_bg, 255)
        from core.hair_renderer import alpha_composite
        return alpha_composite(bg, ov)
