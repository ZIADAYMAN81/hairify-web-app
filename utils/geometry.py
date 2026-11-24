"""
geometry.py — 2-D geometry primitives for Hairify.

Includes:
  - Bezier curve rasterisation (De Casteljau)
  - Scanline polygon fill (edge table algorithm)
  - Convex hull (Graham scan)
  - Ellipse fill
  - Parabola points
"""

import math
import numpy as np
from typing import List, Tuple, Optional


Point = Tuple[float, float]


# ---------------------------------------------------------------------------
# Bezier curves
# ---------------------------------------------------------------------------

def de_casteljau(control_points: List[Point], t: float) -> Point:
    """Evaluate a Bezier curve at parameter t ∈ [0, 1] via De Casteljau."""
    pts = [list(p) for p in control_points]
    n = len(pts)
    for r in range(1, n):
        for i in range(n - r):
            pts[i][0] = (1 - t) * pts[i][0] + t * pts[i + 1][0]
            pts[i][1] = (1 - t) * pts[i][1] + t * pts[i + 1][1]
    return (pts[0][0], pts[0][1])


def bezier_curve(control_points: List[Point], num_points: int = 200) -> List[Point]:
    """Return a list of points along the Bezier curve."""
    return [de_casteljau(control_points, t / (num_points - 1))
            for t in range(num_points)]


def quadratic_bezier(p0: Point, p1: Point, p2: Point,
                     num_points: int = 100) -> List[Point]:
    """Convenience for a quadratic Bezier."""
    return bezier_curve([p0, p1, p2], num_points)


def cubic_bezier(p0: Point, p1: Point, p2: Point, p3: Point,
                 num_points: int = 150) -> List[Point]:
    """Convenience for a cubic Bezier."""
    return bezier_curve([p0, p1, p2, p3], num_points)


# ---------------------------------------------------------------------------
# Polygon rasterisation (scanline fill)
# ---------------------------------------------------------------------------

def _build_edge_table(polygon: List[Point], height: int) -> dict:
    """Build edge table for scanline fill algorithm."""
    ET: dict = {}  # y_min -> list of (x_at_y_min, x_step, y_max)
    n = len(polygon)
    for i in range(n):
        x0, y0 = polygon[i]
        x1, y1 = polygon[(i + 1) % n]
        if int(y0) == int(y1):
            continue  # skip horizontal edges
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        y_min = int(math.ceil(y0))
        y_max = int(math.ceil(y1))
        x_at_ymin = x0 + (y_min - y0) * (x1 - x0) / (y1 - y0)
        dx = (x1 - x0) / (y1 - y0)
        ET.setdefault(y_min, []).append([x_at_ymin, dx, y_max])
    return ET


def fill_polygon(canvas: np.ndarray, polygon: List[Point],
                 color: Tuple, alpha: float = 1.0) -> np.ndarray:
    """
    Fill a polygon on a (H, W, C) uint8 canvas using the scanline algorithm.

    canvas  : (H, W, 4) RGBA uint8 array (modified in-place)
    polygon : list of (x, y) float points
    color   : (R, G, B) tuple 0-255
    alpha   : fill opacity 0-1
    """
    if len(polygon) < 3:
        return canvas
    H, W = canvas.shape[:2]
    ET = _build_edge_table(polygon, H)
    if not ET:
        return canvas
    AET: List = []  # active edge table
    y_min_global = min(ET.keys())
    y_max_global = max(int(math.ceil(p[1])) for p in polygon)

    for y in range(max(0, y_min_global), min(H, y_max_global)):
        # Add new edges from ET
        if y in ET:
            AET.extend(ET[y])
        # Remove expired edges
        AET = [e for e in AET if e[2] > y]
        # Sort by x
        AET.sort(key=lambda e: e[0])
        # Fill pairs
        for k in range(0, len(AET) - 1, 2):
            x_start = int(math.ceil(AET[k][0]))
            x_end = int(math.floor(AET[k + 1][0]))
            x_start = max(0, x_start)
            x_end = min(W - 1, x_end)
            if x_start > x_end:
                continue
            a_byte = int(alpha * 255)
            canvas[y, x_start:x_end + 1, :3] = color[:3]
            canvas[y, x_start:x_end + 1, 3] = a_byte
        # Advance x
        for e in AET:
            e[0] += e[1]
    return canvas


# ---------------------------------------------------------------------------
# Ellipse fill (midpoint algorithm)
# ---------------------------------------------------------------------------

def fill_ellipse(canvas: np.ndarray, cx: int, cy: int,
                 rx: int, ry: int, color: Tuple,
                 alpha: float = 1.0) -> np.ndarray:
    """Fill an axis-aligned ellipse on a (H, W, 4) RGBA canvas."""
    H, W = canvas.shape[:2]
    a_byte = int(alpha * 255)
    y0 = max(0, cy - ry)
    y1 = min(H - 1, cy + ry)
    for y in range(y0, y1 + 1):
        dy = y - cy
        if abs(ry) < 1:
            continue
        ratio = 1.0 - (dy / ry) ** 2
        if ratio < 0:
            continue
        half_w = int(rx * math.sqrt(ratio))
        xs = max(0, cx - half_w)
        xe = min(W - 1, cx + half_w)
        canvas[y, xs:xe + 1, :3] = color[:3]
        canvas[y, xs:xe + 1, 3] = a_byte
    return canvas


# ---------------------------------------------------------------------------
# Stroke / line rasterisation (Bresenham)
# ---------------------------------------------------------------------------

def draw_line(canvas: np.ndarray, x0: int, y0: int,
              x1: int, y1: int, color: Tuple,
              thickness: int = 1, alpha: float = 1.0) -> np.ndarray:
    """Rasterise a thick line using Bresenham's algorithm."""
    H, W = canvas.shape[:2]
    a_byte = int(alpha * 255)
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    r = thickness // 2
    x, y = x0, y0
    while True:
        for ty in range(-r, r + 1):
            for tx in range(-r, r + 1):
                px, py = x + tx, y + ty
                if 0 <= px < W and 0 <= py < H:
                    canvas[py, px, :3] = color[:3]
                    canvas[py, px, 3] = a_byte
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return canvas


def draw_bezier_stroke(canvas: np.ndarray,
                       control_points: List[Point],
                       color: Tuple,
                       thickness: int = 2,
                       alpha: float = 1.0,
                       num_points: int = 200) -> np.ndarray:
    """Draw a stroked Bezier curve onto the canvas."""
    pts = bezier_curve(control_points, num_points)
    for i in range(len(pts) - 1):
        x0, y0 = int(pts[i][0]), int(pts[i][1])
        x1, y1 = int(pts[i + 1][0]), int(pts[i + 1][1])
        draw_line(canvas, x0, y0, x1, y1, color, thickness, alpha)
    return canvas


# ---------------------------------------------------------------------------
# Parabola helpers (for hairline curve)
# ---------------------------------------------------------------------------

def parabola_points(vertex: Point, width: float, height: float,
                    num_points: int = 20,
                    open_downward: bool = True) -> List[Point]:
    """
    Return points along a parabola centred at `vertex`.

    vertex       : (cx, cy) — tip of the parabola
    width        : total horizontal span
    height       : vertical distance from vertex to edge
    open_downward: if True parabola opens down (hair arch shape)
    """
    cx, cy = vertex
    points = []
    sign = -1 if open_downward else 1
    for i in range(num_points):
        t = -1.0 + 2.0 * i / (num_points - 1)  # t ∈ [-1, 1]
        x = cx + t * (width / 2)
        y = cy + sign * height * (1 - t ** 2)
        points.append((x, y))
    return points


# ---------------------------------------------------------------------------
# Convex hull (Graham scan)
# ---------------------------------------------------------------------------

def convex_hull(points: List[Point]) -> List[Point]:
    """Return the convex hull of a set of 2-D points (Graham scan)."""
    if len(points) < 3:
        return points
    pts = sorted(set(points))
    # Lower hull
    lower: List[Point] = []
    for p in pts:
        while len(lower) >= 2 and cross2d(
                (lower[-1][0] - lower[-2][0], lower[-1][1] - lower[-2][1]),
                (p[0] - lower[-2][0], p[1] - lower[-2][1])) <= 0:
            lower.pop()
        lower.append(p)
    # Upper hull
    upper: List[Point] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross2d(
                (upper[-1][0] - upper[-2][0], upper[-1][1] - upper[-2][1]),
                (p[0] - upper[-2][0], p[1] - upper[-2][1])) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def cross2d(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


# ---------------------------------------------------------------------------
# Circle / arc helpers
# ---------------------------------------------------------------------------

def circle_points(cx: float, cy: float, r: float,
                  start_deg: float = 0, end_deg: float = 360,
                  num_points: int = 60) -> List[Point]:
    """Return points along a circular arc."""
    pts = []
    for i in range(num_points):
        t = start_deg + (end_deg - start_deg) * i / (num_points - 1)
        rad = math.radians(t)
        pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
    return pts


def make_rounded_rect_polygon(x: float, y: float, w: float, h: float,
                              radius: float, num_arc: int = 8) -> List[Point]:
    """Return polygon points for a rounded rectangle."""
    r = min(radius, w / 2, h / 2)
    pts: List[Point] = []
    # Four corners, each with a small arc
    corners = [
        (x + r,     y + r,     180, 270),
        (x + w - r, y + r,     270, 360),
        (x + w - r, y + h - r,   0,  90),
        (x + r,     y + h - r,  90, 180),
    ]
    for cx, cy, s, e in corners:
        pts.extend(circle_points(cx, cy, r, s, e, num_arc))
    return pts
