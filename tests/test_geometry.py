"""Tests for geometry primitives."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from utils.geometry import (
    de_casteljau, bezier_curve, fill_polygon,
    fill_ellipse, parabola_points, convex_hull
)
from core.image_utils import new_canvas


def test_de_casteljau_endpoints():
    """Bezier at t=0 should return p0, at t=1 should return p3."""
    p0, p1, p2, p3 = (0, 0), (1, 2), (3, 2), (4, 0)
    assert de_casteljau([p0, p1, p2, p3], 0.0) == (0.0, 0.0)
    x, y = de_casteljau([p0, p1, p2, p3], 1.0)
    assert abs(x - 4.0) < 1e-9 and abs(y - 0.0) < 1e-9


def test_bezier_curve_length():
    pts = bezier_curve([(0, 0), (50, 100), (100, 0)], num_points=50)
    assert len(pts) == 50


def test_fill_polygon_writes_pixels():
    canvas = new_canvas(100, 100, (0, 0, 0, 0))
    poly = [(20, 20), (80, 20), (80, 80), (20, 80)]
    fill_polygon(canvas, poly, (255, 0, 0), alpha=1.0)
    # Centre pixel should be red with full alpha
    assert canvas[50, 50, 0] == 255
    assert canvas[50, 50, 3] == 255
    # Corner pixel should be transparent
    assert canvas[0, 0, 3] == 0


def test_fill_ellipse_writes_pixels():
    canvas = new_canvas(100, 100, (0, 0, 0, 0))
    fill_ellipse(canvas, 50, 50, 30, 20, (0, 255, 0), alpha=1.0)
    assert canvas[50, 50, 1] == 255   # centre is green
    assert canvas[50, 50, 3] == 255   # fully opaque


def test_parabola_points_count():
    pts = parabola_points((100, 50), 200, 30, num_points=10)
    assert len(pts) == 10


def test_parabola_vertex():
    """Vertex of a downward parabola should be the min-y point."""
    pts = parabola_points((100, 50), 200, 30, num_points=21, open_downward=True)
    ys = [p[1] for p in pts]
    # Midpoint t=0 gives minimum y (vertex)
    assert ys[10] == min(ys)


def test_convex_hull_square():
    pts = [(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)]
    hull = convex_hull(pts)
    # Hull should not include interior point
    assert (0.5, 0.5) not in hull
    assert len(hull) == 4


if __name__ == "__main__":
    test_de_casteljau_endpoints()
    test_bezier_curve_length()
    test_fill_polygon_writes_pixels()
    test_fill_ellipse_writes_pixels()
    test_parabola_points_count()
    test_parabola_vertex()
    test_convex_hull_square()
    print("All geometry tests passed!")
