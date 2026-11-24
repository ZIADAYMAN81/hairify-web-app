"""Tests for the hair renderer."""

import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.hair_renderer import alpha_composite, make_split_view
from core.image_utils import new_canvas


def _make_rgba(H, W, color):
    canvas = new_canvas(W, H, color)
    return canvas


def test_alpha_composite_opaque_src():
    """Fully opaque src should completely replace dst."""
    dst = _make_rgba(10, 10, (255, 0, 0, 255))   # red
    src = _make_rgba(10, 10, (0, 255, 0, 255))   # green
    out = alpha_composite(dst, src)
    # Output should be green
    assert out[5, 5, 1] > 200, "Expected green channel dominant"
    assert out[5, 5, 0] < 20,  "Expected red channel suppressed"


def test_alpha_composite_transparent_src():
    """Fully transparent src should leave dst unchanged."""
    dst = _make_rgba(10, 10, (200, 100, 50, 255))
    src = _make_rgba(10, 10, (0, 0, 0, 0))         # transparent
    out = alpha_composite(dst, src)
    assert out[5, 5, 0] == 200
    assert out[5, 5, 1] == 100
    assert out[5, 5, 2] == 50


def test_alpha_composite_semi():
    """Semi-transparent src should blend."""
    dst = _make_rgba(10, 10, (0, 0, 0, 255))      # black
    src = _make_rgba(10, 10, (255, 255, 255, 128)) # white, 50% opacity
    out = alpha_composite(dst, src)
    # Result should be grey-ish
    assert 100 < out[5, 5, 0] < 200, "Expected blend"


def test_split_view_left_is_base():
    """Left half of split view should match base."""
    base = _make_rgba(100, 100, (200, 0, 0, 255))
    comp = _make_rgba(100, 100, (0, 200, 0, 255))
    split = make_split_view(base, comp, split_ratio=0.5)
    # Left quarter should be base (red)
    assert split[50, 10, 0] > 150, "Left should be red (base)"


def test_split_view_right_is_composited():
    """Right half of split view should match composited."""
    base = _make_rgba(100, 100, (200, 0, 0, 255))
    comp = _make_rgba(100, 100, (0, 200, 0, 255))
    split = make_split_view(base, comp, split_ratio=0.5)
    # Right quarter should be composited (green)
    assert split[50, 90, 1] > 150, "Right should be green (composited)"


if __name__ == "__main__":
    test_alpha_composite_opaque_src()
    test_alpha_composite_transparent_src()
    test_alpha_composite_semi()
    test_split_view_left_is_base()
    test_split_view_right_is_composited()
    print("All hair renderer tests passed!")
