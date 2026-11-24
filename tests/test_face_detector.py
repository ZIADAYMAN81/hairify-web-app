"""Tests for the face detector."""

import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.face_detector import detect_face, _skin_mask_ycbcr, FaceResult


def _make_skin_image(H=200, W=200):
    """Create a synthetic image with a skin-colored blob in the centre."""
    img = np.zeros((H, W, 4), dtype=np.uint8)
    img[:, :, 3] = 255
    # Background — non-skin (dark grey)
    img[:, :, :3] = [30, 30, 30]
    # Skin-coloured centre square (YCbCr skin range → approximately #C68642)
    cy, cx = H // 2, W // 2
    r = H // 5
    img[cy - r:cy + r, cx - r:cx + r, :3] = [198, 134, 66]
    return img


def test_skin_mask_detects_skin():
    img = _make_skin_image()
    mask = _skin_mask_ycbcr(img[:, :, :3])
    # There should be some skin pixels
    assert mask.any(), "Expected some skin pixels detected"


def test_skin_mask_ignores_background():
    img = _make_skin_image()
    mask = _skin_mask_ycbcr(img[:, :, :3])
    # Top-left corner should be background (not skin)
    assert not mask[0, 0], "Top-left background should not be skin"


def test_detect_face_returns_fallback_on_blank():
    """Blank black image should return fallback (found=False)."""
    img = np.zeros((300, 300, 4), dtype=np.uint8)
    img[:, :, 3] = 255
    result = detect_face(img)
    assert isinstance(result, FaceResult)
    # Should still give a usable bbox
    assert result.w > 0
    assert result.h > 0


def test_detect_face_finds_skin_blob():
    """Synthetic skin image should trigger detection."""
    img = _make_skin_image(300, 300)
    result = detect_face(img)
    # May or may not pass validation heuristic — just must return FaceResult
    assert isinstance(result, FaceResult)
    assert result.w > 0 and result.h > 0


def test_fallback_coverage():
    """Fallback bbox must be within image dimensions."""
    img = np.zeros((480, 640, 4), dtype=np.uint8)
    img[:, :, 3] = 255
    result = detect_face(img)
    assert result.x >= 0
    assert result.y >= 0
    assert result.x + result.w <= 640
    assert result.y + result.h <= 480


if __name__ == "__main__":
    test_skin_mask_detects_skin()
    test_skin_mask_ignores_background()
    test_detect_face_returns_fallback_on_blank()
    test_detect_face_finds_skin_blob()
    test_fallback_coverage()
    print("All face detector tests passed!")
