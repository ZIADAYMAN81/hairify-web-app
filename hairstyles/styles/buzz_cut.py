"""buzz_cut.py — Very short buzz cut hairstyle overlay."""

import numpy as np
from hairstyles.base_style import HairstyleBase
from utils.geometry import fill_ellipse, fill_polygon


class BuzzCut(HairstyleBase):
    name = "Buzz Cut"
    description = "Very short, uniform buzz all over"
    gender = "male"
    length = "short"
    default_color = (55, 32, 12)
    thumb_bg = (22, 14, 30)

    def generate_overlay(self, width: int, height: int) -> np.ndarray:
        canvas = self.blank(width, height)
        c = self.default_color
        W, H = width, height

        # Thin cap conforming to head shape
        fill_ellipse(canvas, W // 2, int(H * 0.18),
                     int(W * 0.44), int(H * 0.22), c, alpha=1.0)

        # Thin strip at temples
        left = [
            (W * 0.06, H * 0.14), (W * 0.03, H * 0.45),
            (W * 0.12, H * 0.50), (W * 0.22, H * 0.44),
            (W * 0.24, H * 0.22), (W * 0.16, H * 0.10),
        ]
        fill_polygon(canvas, left, c, alpha=0.90)
        right = [
            (W * 0.94, H * 0.14), (W * 0.97, H * 0.45),
            (W * 0.88, H * 0.50), (W * 0.78, H * 0.44),
            (W * 0.76, H * 0.22), (W * 0.84, H * 0.10),
        ]
        fill_polygon(canvas, right, c, alpha=0.90)

        # Stubble texture (tiny dots over cap)
        rng = np.random.default_rng(42)
        for _ in range(300):
            tx = int(rng.uniform(W * 0.20, W * 0.80))
            ty = int(rng.uniform(H * 0.02, H * 0.35))
            if 0 <= tx < W and 0 <= ty < H and canvas[ty, tx, 3] > 0:
                shade = (min(255, c[0] + int(rng.integers(-10, 20))),
                         min(255, c[1] + int(rng.integers(-5, 10))),
                         c[2])
                canvas[ty, tx] = (*shade, 200)

        return canvas
