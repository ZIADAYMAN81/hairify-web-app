"""
landmark_finder.py — Estimate hairline and forehead landmarks from a face bbox.

Given the face bounding box from face_detector, this module estimates:
  - The top of the head / start of the hairline
  - 5 parabolic anchor points along the hairline arc
  - Face width, height, and tilt estimate (symmetric assumption)
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

from utils.geometry import parabola_points


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class LandmarkResult:
    """Estimated facial landmark positions for hair overlay placement."""
    # Centre top of head (where hair starts)
    head_top: Tuple[float, float] = (0.0, 0.0)
    # Forehead centre (slightly below head_top)
    forehead_centre: Tuple[float, float] = (0.0, 0.0)
    # 5 hairline anchor points (parabolic arc)
    hairline_points: List[Tuple[float, float]] = field(default_factory=list)
    # Face dimensions
    face_width: float = 0.0
    face_height: float = 0.0
    # Face centre
    face_cx: float = 0.0
    face_cy: float = 0.0
    # Recommended overlay position and size
    overlay_x: float = 0.0   # left edge of where hair overlay should start
    overlay_y: float = 0.0   # top edge
    overlay_w: float = 0.0
    overlay_h: float = 0.0


# ---------------------------------------------------------------------------
# Proportional constants (relative to face height)
# ---------------------------------------------------------------------------

# How far above the top of the face bbox the hair crown is estimated
_HEAD_TOP_OFFSET_RATIO = 0.12   # head crown is ~12% of face_h above bbox top
# Width of hairline relative to face width
_HAIRLINE_WIDTH_RATIO  = 1.10
# Height of the parabolic hairline arch
_HAIRLINE_ARCH_RATIO   = 0.08   # arch height as fraction of face_h
# Overlay height: covers head + hair (generous)
_OVERLAY_H_RATIO       = 0.95
# Overlay width: slightly wider than face
_OVERLAY_W_RATIO       = 1.25


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_landmarks(face_x: int, face_y: int,
                   face_w: int, face_h: int) -> LandmarkResult:
    """
    Estimate hair-placement landmarks from the face bounding box.

    Parameters
    ----------
    face_x, face_y : top-left corner of face bbox
    face_w, face_h : face bbox dimensions

    Returns
    -------
    LandmarkResult with all estimated positions
    """
    # Face centre
    cx = face_x + face_w / 2
    cy = face_y + face_h / 2

    # Head crown — slightly above the detected face bbox
    head_top_y = face_y - _HEAD_TOP_OFFSET_RATIO * face_h
    head_top = (cx, head_top_y)

    # Forehead centre — 15% below head_top
    forehead_y = head_top_y + 0.15 * face_h
    forehead_centre = (cx, forehead_y)

    # Hairline arc: 5 anchor points along a parabola
    hairline_width = face_w * _HAIRLINE_WIDTH_RATIO
    arch_height = face_h * _HAIRLINE_ARCH_RATIO
    hairline_pts = _sample_hairline_arc(cx, head_top_y,
                                        hairline_width, arch_height)

    # Overlay bounding rect
    ov_w = face_w * _OVERLAY_W_RATIO
    ov_h = face_h * _OVERLAY_H_RATIO
    ov_x = cx - ov_w / 2
    ov_y = head_top_y - 0.08 * face_h  # a bit above head_top

    return LandmarkResult(
        head_top=head_top,
        forehead_centre=forehead_centre,
        hairline_points=hairline_pts,
        face_width=float(face_w),
        face_height=float(face_h),
        face_cx=cx,
        face_cy=cy,
        overlay_x=ov_x,
        overlay_y=ov_y,
        overlay_w=ov_w,
        overlay_h=ov_h,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sample_hairline_arc(cx: float, cy: float,
                          width: float, arch: float,
                          n: int = 5) -> List[Tuple[float, float]]:
    """
    Return n evenly-spaced points along a downward-opening parabola
    that models the hairline arc.
    The vertex of the parabola is at (cx, cy) — the crown of the head.
    """
    pts = parabola_points(
        vertex=(cx, cy),
        width=width,
        height=arch,
        num_points=n,
        open_downward=False,   # opens upward → arc dips downward from crown
    )
    return pts
