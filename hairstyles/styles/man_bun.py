"""man_bun.py — Man bun / top knot hairstyle overlay."""

import numpy as np
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_ellipse, fill_polygon


class ManBun(HairstyleBase):
    name = "Man Bun"
    description = "Pulled-back top knot with faded sides"
    gender = "male"
    length = "medium"
    default_color = (40, 22, 8)
    thumb_bg = (20, 14, 30)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        dark = (max(0, c[0] - 15), max(0, c[1] - 8), max(0, c[2] - 3))
        W, H = width, height

        # ---- Short faded sides ----
        left_side = [
            (W * 0.05, H * 0.15),
            (W * 0.03, H * 0.50),
            (W * 0.10, H * 0.58),
            (W * 0.22, H * 0.52),
            (W * 0.26, H * 0.30),
            (W * 0.20, H * 0.10),
        ]
        fill_polygon(canvas, left_side, dark, alpha=0.75)

        right_side = [
            (W * 0.95, H * 0.15),
            (W * 0.97, H * 0.50),
            (W * 0.90, H * 0.58),
            (W * 0.78, H * 0.52),
            (W * 0.74, H * 0.30),
            (W * 0.80, H * 0.10),
        ]
        fill_polygon(canvas, right_side, dark, alpha=0.75)

        # ---- Top long section going up to bun ----
        top_section = [
            (W * 0.28, H * 0.10),
            (W * 0.72, H * 0.10),
            (W * 0.68, H * 0.02),
            (W * 0.50, H * 0.00),
            (W * 0.32, H * 0.02),
        ]
        fill_polygon(canvas, top_section, c, alpha=1.0)

        # ---- Bun knot (ellipse at the very top) ----
        fill_ellipse(canvas, W // 2, int(H * 0.08),
                     int(W * 0.14), int(H * 0.10), c, alpha=1.0)
        # Bun highlight ring
        fill_ellipse(canvas, W // 2, int(H * 0.08),
                     int(W * 0.10), int(H * 0.07),
                     (min(255, c[0] + 30), min(255, c[1] + 15), c[2]),
                     alpha=0.45)

        # ---- Hair tie (dark band around bun) ----
        tie = [
            (W * 0.40, H * 0.14),
            (W * 0.60, H * 0.14),
            (W * 0.60, H * 0.17),
            (W * 0.40, H * 0.17),
        ]
        fill_polygon(canvas, tie, (20, 10, 5), alpha=1.0)

        return canvas
