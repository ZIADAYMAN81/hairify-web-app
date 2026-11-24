"""mohawk.py — Mohawk hairstyle overlay."""

import numpy as np
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_polygon, fill_ellipse


class Mohawk(HairstyleBase):
    name = "Mohawk"
    description = "Central raised ridge with shaved sides"
    gender = "male"
    length = "medium"
    default_color = (30, 15, 5)
    thumb_bg = (18, 10, 28)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height

        # Central strip
        strip = [
            (W * 0.40, H * 0.60), (W * 0.60, H * 0.60),
            (W * 0.58, H * 0.00), (W * 0.42, H * 0.00),
        ]
        fill_polygon(canvas, strip, c, alpha=1.0)

        # Spiky top (triangle peaks)
        for i, px in enumerate([0.44, 0.50, 0.56]):
            tip_y = -0.06 - i * 0.02 if i == 1 else -0.03
            spike = [
                (W * (px - 0.06), H * 0.10),
                (W * px,          H * tip_y),
                (W * (px + 0.06), H * 0.10),
            ]
            fill_polygon(canvas, spike, c, alpha=1.0)

        return canvas
