"""long_straight.py — Shoulder-length straight hair overlay."""

import numpy as np
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_polygon, fill_ellipse


class LongStraight(HairstyleBase):
    name = "Long Straight"
    description = "Sleek, shoulder-length straight hair"
    gender = "female"
    length = "long"
    default_color = (35, 18, 8)
    thumb_bg = (22, 14, 32)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height

        # ---- Crown cap ----
        fill_ellipse(canvas, W // 2, int(H * 0.16),
                     int(W * 0.42), int(H * 0.18), c, alpha=1.0)

        # ---- Left long panel ----
        left = [
            (W * 0.08, H * 0.14),
            (W * 0.04, H * 0.55),
            (W * 0.06, H * 0.95),
            (W * 0.18, H * 0.96),
            (W * 0.24, H * 0.90),
            (W * 0.28, H * 0.55),
            (W * 0.30, H * 0.25),
            (W * 0.22, H * 0.08),
        ]
        fill_polygon(canvas, left, c, alpha=1.0)

        # ---- Right long panel ----
        right = [
            (W * 0.92, H * 0.14),
            (W * 0.96, H * 0.55),
            (W * 0.94, H * 0.95),
            (W * 0.82, H * 0.96),
            (W * 0.76, H * 0.90),
            (W * 0.72, H * 0.55),
            (W * 0.70, H * 0.25),
            (W * 0.78, H * 0.08),
        ]
        fill_polygon(canvas, right, c, alpha=1.0)

        # ---- Top fill ----
        top = [
            (W * 0.22, H * 0.02),
            (W * 0.50, H * 0.00),
            (W * 0.78, H * 0.02),
            (W * 0.82, H * 0.12),
            (W * 0.50, H * 0.07),
            (W * 0.18, H * 0.12),
        ]
        fill_polygon(canvas, top, c, alpha=1.0)

        # ---- Centre parting line (slightly lighter) ----
        part_color = (c[0] + 20, c[1] + 10, c[2] + 5)
        part = [
            (W * 0.47, H * 0.00),
            (W * 0.53, H * 0.00),
            (W * 0.53, H * 0.18),
            (W * 0.47, H * 0.18),
        ]
        fill_polygon(canvas, part, part_color, alpha=0.5)

        return canvas
