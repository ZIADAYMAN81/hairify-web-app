"""pixie_cut.py — Short textured pixie cut overlay."""

import numpy as np
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_polygon, fill_ellipse


class PixieCut(HairstyleBase):
    name = "Pixie Cut"
    description = "Short, textured pixie with side-swept fringe"
    gender = "female"
    length = "short"
    default_color = (80, 40, 15)
    thumb_bg = (30, 18, 38)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height

        # ---- Crown cap ----
        fill_ellipse(canvas, W // 2, int(H * 0.18), int(W * 0.40), int(H * 0.20),
                     c, alpha=1.0)

        # ---- Short sides ----
        left_side = [
            (W * 0.10, H * 0.15),
            (W * 0.06, H * 0.42),
            (W * 0.13, H * 0.50),
            (W * 0.28, H * 0.46),
            (W * 0.32, H * 0.25),
            (W * 0.20, H * 0.08),
        ]
        fill_polygon(canvas, left_side, c, alpha=1.0)

        right_side = [
            (W * 0.90, H * 0.15),
            (W * 0.94, H * 0.42),
            (W * 0.87, H * 0.50),
            (W * 0.72, H * 0.46),
            (W * 0.68, H * 0.25),
            (W * 0.80, H * 0.08),
        ]
        fill_polygon(canvas, right_side, c, alpha=1.0)

        # ---- Fringe / wispy top ----
        fringe = [
            (W * 0.15, H * 0.05),
            (W * 0.50, H * 0.00),
            (W * 0.80, H * 0.05),
            (W * 0.75, H * 0.14),
            (W * 0.50, H * 0.10),
            (W * 0.25, H * 0.14),
        ]
        fill_polygon(canvas, fringe, c, alpha=1.0)

        # ---- Wispy texture strands (thin ellipses) ----
        for i, (bx, by) in enumerate([
            (0.30, 0.38), (0.42, 0.35), (0.55, 0.36), (0.65, 0.38)
        ]):
            fill_ellipse(canvas, int(W * bx), int(H * by),
                         int(W * 0.05), int(H * 0.04), c, alpha=0.65)

        return canvas
