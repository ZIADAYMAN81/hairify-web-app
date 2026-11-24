"""bob_cut.py — Chin-length bob hairstyle overlay."""

import numpy as np
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_polygon, cubic_bezier, fill_ellipse


class BobCut(HairstyleBase):
    name = "Bob Cut"
    description = "Classic chin-length straight bob"
    gender = "female"
    length = "medium"
    default_color = (50, 25, 10)
    thumb_bg = (25, 15, 35)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height

        # ---- Top cap (ellipse covering top of head) ----
        fill_ellipse(canvas, W // 2, int(H * 0.22), int(W * 0.42), int(H * 0.22),
                     c, alpha=1.0)

        # ---- Left side panel ----
        left = [
            (W * 0.08, H * 0.20),
            (W * 0.05, H * 0.55),
            (W * 0.10, H * 0.72),
            (W * 0.22, H * 0.75),
            (W * 0.35, H * 0.70),
            (W * 0.40, H * 0.40),
            (W * 0.30, H * 0.10),
            (W * 0.15, H * 0.08),
        ]
        fill_polygon(canvas, left, c, alpha=1.0)

        # ---- Right side panel ----
        right = [
            (W * 0.92, H * 0.20),
            (W * 0.95, H * 0.55),
            (W * 0.90, H * 0.72),
            (W * 0.78, H * 0.75),
            (W * 0.65, H * 0.70),
            (W * 0.60, H * 0.40),
            (W * 0.70, H * 0.10),
            (W * 0.85, H * 0.08),
        ]
        fill_polygon(canvas, right, c, alpha=1.0)

        # ---- Top fill (crown) ----
        crown = [
            (W * 0.20, H * 0.02),
            (W * 0.50, H * 0.00),
            (W * 0.80, H * 0.02),
            (W * 0.85, H * 0.12),
            (W * 0.50, H * 0.08),
            (W * 0.15, H * 0.12),
        ]
        fill_polygon(canvas, crown, c, alpha=1.0)

        # ---- Bottom fringe line (straight bob edge) ----
        fringe = [
            (W * 0.10, H * 0.70),
            (W * 0.22, H * 0.76),
            (W * 0.50, H * 0.78),
            (W * 0.78, H * 0.76),
            (W * 0.90, H * 0.70),
            (W * 0.90, H * 0.74),
            (W * 0.78, H * 0.80),
            (W * 0.50, H * 0.82),
            (W * 0.22, H * 0.80),
            (W * 0.10, H * 0.74),
        ]
        fill_polygon(canvas, fringe, c, alpha=1.0)

        return canvas
