"""curly_afro.py — Round, voluminous afro hairstyle overlay."""

import numpy as np
import math
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_ellipse, fill_polygon, circle_points


class CurlyAfro(HairstyleBase):
    name = "Curly Afro"
    description = "Big, round voluminous natural afro"
    gender = "unisex"
    length = "medium"
    default_color = (25, 12, 5)
    thumb_bg = (20, 12, 28)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height

        # ---- Main afro ball ----
        fill_ellipse(canvas, W // 2, int(H * 0.30),
                     int(W * 0.46), int(H * 0.35), c, alpha=1.0)

        # ---- Bumpy perimeter (simulate curls) ----
        num_bumps = 22
        cx, cy = W / 2, H * 0.30
        rx, ry = W * 0.46, H * 0.35
        for i in range(num_bumps):
            angle = 2 * math.pi * i / num_bumps
            # Alternate bump size for natural look
            bump_r = (0.07 if i % 2 == 0 else 0.05) * min(W, H)
            bx = cx + rx * math.cos(angle) * 0.92
            by = cy + ry * math.sin(angle) * 0.92
            fill_ellipse(canvas, int(bx), int(by),
                         int(bump_r), int(bump_r), c, alpha=1.0)

        # ---- Thin neckline strip ----
        neck = [
            (W * 0.35, H * 0.60),
            (W * 0.65, H * 0.60),
            (W * 0.62, H * 0.68),
            (W * 0.38, H * 0.68),
        ]
        fill_polygon(canvas, neck, c, alpha=0.85)

        return canvas
