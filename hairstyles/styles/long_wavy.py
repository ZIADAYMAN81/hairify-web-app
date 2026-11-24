"""long_wavy.py — Long flowing wavy hair overlay."""

import numpy as np
import math
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_polygon, fill_ellipse, cubic_bezier


class LongWavy(HairstyleBase):
    name = "Long Wavy"
    description = "Flowing mid-back wavy hair"
    gender = "female"
    length = "long"
    default_color = (55, 28, 10)
    thumb_bg = (28, 15, 35)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height

        # ---- Crown ----
        fill_ellipse(canvas, W // 2, int(H * 0.15),
                     int(W * 0.43), int(H * 0.17), c, alpha=1.0)

        top = [
            (W * 0.20, H * 0.01),
            (W * 0.50, H * 0.00),
            (W * 0.80, H * 0.01),
            (W * 0.82, H * 0.10),
            (W * 0.50, H * 0.06),
            (W * 0.18, H * 0.10),
        ]
        fill_polygon(canvas, top, c, alpha=1.0)

        # ---- Left wavy panel ----
        # Build wavy outline using sinusoidal x offset
        left_pts = []
        for i in range(30):
            t = i / 29.0
            y = H * (0.10 + t * 0.88)
            wave = math.sin(t * math.pi * 3.5) * W * 0.04
            x = W * 0.06 + wave
            left_pts.append((x, y))
        # Close the polygon on the inside
        for i in range(29, -1, -1):
            t = i / 29.0
            y = H * (0.10 + t * 0.88)
            wave = math.sin(t * math.pi * 3.5) * W * 0.02
            x = W * 0.26 + wave
            left_pts.append((x, y))
        fill_polygon(canvas, left_pts, c, alpha=1.0)

        # ---- Right wavy panel ----
        right_pts = []
        for i in range(30):
            t = i / 29.0
            y = H * (0.10 + t * 0.88)
            wave = math.sin(t * math.pi * 3.5 + 1.0) * W * 0.04
            x = W * 0.94 - wave
            right_pts.append((x, y))
        for i in range(29, -1, -1):
            t = i / 29.0
            y = H * (0.10 + t * 0.88)
            wave = math.sin(t * math.pi * 3.5 + 1.0) * W * 0.02
            x = W * 0.74 - wave
            right_pts.append((x, y))
        fill_polygon(canvas, right_pts, c, alpha=1.0)

        # ---- Strand highlights (semi-transparent lighter lines) ----
        highlight = (min(255, c[0] + 35), min(255, c[1] + 18), min(255, c[2] + 8))
        for offset in [0.32, 0.68]:
            strand = []
            for i in range(20):
                t = i / 19.0
                y = H * (0.05 + t * 0.85)
                x = W * offset + math.sin(t * math.pi * 4) * W * 0.02
                strand.append((int(x), int(y)))
            for pt in strand:
                x, y = pt
                if 0 <= x < W and 0 <= y < H and canvas[y, x, 3] > 0:
                    canvas[y, x] = (*highlight, 160)

        return canvas
