"""cornrows.py — Cornrow braids hairstyle overlay."""

import numpy as np
import math
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_polygon, fill_ellipse


class Cornrows(HairstyleBase):
    name = "Cornrows"
    description = "Tight parallel cornrow braids"
    gender = "unisex"
    length = "short"
    default_color = (30, 15, 5)
    thumb_bg = (20, 12, 28)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        alt = (min(255, c[0] + 18), min(255, c[1] + 9), min(255, c[2] + 4))
        W, H = width, height

        # Top cap
        fill_ellipse(canvas, W // 2, int(H * 0.18),
                     int(W * 0.42), int(H * 0.20), c, alpha=1.0)
        top = [
            (W * 0.18, H * 0.01), (W * 0.50, H * 0.00),
            (W * 0.82, H * 0.01), (W * 0.84, H * 0.12),
            (W * 0.50, H * 0.07), (W * 0.16, H * 0.12),
        ]
        fill_polygon(canvas, top, c, alpha=1.0)

        # 6 braided rows front to back
        num_rows = 6
        for i in range(num_rows):
            t = i / (num_rows - 1)
            x_center = W * (0.22 + t * 0.56)
            row_color = alt if i % 2 == 0 else c
            # Each row is a narrow rounded strip
            row_w = int(W * 0.055)
            for seg in range(12):
                s = seg / 11.0
                y = int(H * (0.05 + s * 0.48))
                bead_h = int(H * 0.04)
                fill_ellipse(canvas, int(x_center), y,
                             row_w // 2, bead_h, row_color, alpha=1.0)

        # Side flaps
        left = [
            (W * 0.06, H * 0.12), (W * 0.02, H * 0.48),
            (W * 0.12, H * 0.55), (W * 0.22, H * 0.48),
            (W * 0.22, H * 0.18),
        ]
        fill_polygon(canvas, left, c, alpha=0.85)
        right = [
            (W * 0.94, H * 0.12), (W * 0.98, H * 0.48),
            (W * 0.88, H * 0.55), (W * 0.78, H * 0.48),
            (W * 0.78, H * 0.18),
        ]
        fill_polygon(canvas, right, c, alpha=0.85)

        return canvas
