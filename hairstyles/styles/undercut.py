"""undercut.py — Faded sides with longer top hairstyle overlay."""

import numpy as np
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_polygon, fill_ellipse


class Undercut(HairstyleBase):
    name = "Undercut"
    description = "Faded sides with swept longer top"
    gender = "male"
    length = "medium"
    default_color = (45, 25, 10)
    thumb_bg = (22, 14, 32)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height
        fade = (max(0, c[0] - 20), max(0, c[1] - 10), max(0, c[2] - 5))

        left_fade = [
            (W * 0.04, H * 0.20), (W * 0.02, H * 0.55),
            (W * 0.10, H * 0.62), (W * 0.20, H * 0.55),
            (W * 0.24, H * 0.35), (W * 0.16, H * 0.12),
        ]
        fill_polygon(canvas, left_fade, fade, alpha=0.70)

        right_fade = [
            (W * 0.96, H * 0.20), (W * 0.98, H * 0.55),
            (W * 0.90, H * 0.62), (W * 0.80, H * 0.55),
            (W * 0.76, H * 0.35), (W * 0.84, H * 0.12),
        ]
        fill_polygon(canvas, right_fade, fade, alpha=0.70)

        top = [
            (W * 0.20, H * 0.02), (W * 0.50, H * 0.00),
            (W * 0.82, H * 0.04), (W * 0.80, H * 0.28),
            (W * 0.62, H * 0.32), (W * 0.50, H * 0.30),
            (W * 0.22, H * 0.28),
        ]
        fill_polygon(canvas, top, c, alpha=1.0)

        fill_ellipse(canvas, W // 2, int(H * 0.14),
                     int(W * 0.38), int(H * 0.15), c, alpha=1.0)

        sweep = [
            (W * 0.45, H * 0.02), (W * 0.80, H * 0.06),
            (W * 0.78, H * 0.14), (W * 0.50, H * 0.10),
        ]
        lighter = (min(255, c[0] + 25), min(255, c[1] + 12), c[2])
        fill_polygon(canvas, sweep, lighter, alpha=0.50)
        return canvas
