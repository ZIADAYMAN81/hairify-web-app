"""
math_utils.py — Low-level math primitives for Hairify.

All operations are implemented from scratch using only NumPy.
"""

import numpy as np
from typing import Tuple, List


# ---------------------------------------------------------------------------
# Vector / scalar helpers
# ---------------------------------------------------------------------------

def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a scalar value to [lo, hi]."""
    return max(lo, min(hi, value))


def clamp_array(arr: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Clamp every element of a NumPy array to [lo, hi]."""
    return np.clip(arr, lo, hi)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t ∈ [0, 1]."""
    return a + t * (b - a)


def lerp_array(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    """Element-wise linear interpolation."""
    return a + t * (b - a)


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Return unit vector of v.  Returns zero vector if magnitude is 0."""
    mag = np.linalg.norm(v)
    return v / mag if mag > 1e-12 else np.zeros_like(v)


def dot2d(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """2-D dot product."""
    return a[0] * b[0] + a[1] * b[1]


def cross2d(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """2-D cross product (scalar z-component)."""
    return a[0] * b[1] - a[1] * b[0]


# ---------------------------------------------------------------------------
# Color-space conversions (all matrices from ITU / IEC standards)
# ---------------------------------------------------------------------------

_RGB_TO_YCBCR_MAT = np.array([
    [ 0.299,     0.587,     0.114   ],
    [-0.168736, -0.331264,  0.5     ],
    [ 0.5,      -0.418688, -0.081312],
], dtype=np.float64)

_YCBCR_TO_RGB_MAT = np.linalg.inv(_RGB_TO_YCBCR_MAT)

_YCBCR_OFFSET = np.array([0.0, 128.0, 128.0], dtype=np.float64)


def rgb_to_ycbcr(rgb: np.ndarray) -> np.ndarray:
    """
    Convert an (H, W, 3) uint8 RGB array to float64 YCbCr [0-255 range].
    Y  ∈ [16, 235]
    Cb ∈ [16, 240]
    Cr ∈ [16, 240]
    """
    f = rgb.astype(np.float64)
    return f @ _RGB_TO_YCBCR_MAT.T + _YCBCR_OFFSET


def ycbcr_to_rgb(ycbcr: np.ndarray) -> np.ndarray:
    """Convert float64 YCbCr back to uint8 RGB."""
    f = ycbcr - _YCBCR_OFFSET
    rgb = f @ _YCBCR_TO_RGB_MAT.T
    return clamp_array(rgb, 0, 255).astype(np.uint8)


# --- LAB conversion (D65 white point) ---

_D65_WHITE = np.array([0.95047, 1.00000, 1.08883], dtype=np.float64)


def _gamma_expand_srgb(c: np.ndarray) -> np.ndarray:
    """Linearise sRGB values (inverse gamma)."""
    c = c / 255.0
    linear = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return linear


def _gamma_compress_srgb(c: np.ndarray) -> np.ndarray:
    """Apply sRGB gamma."""
    compressed = np.where(
        c <= 0.0031308,
        c * 12.92,
        1.055 * np.power(np.clip(c, 0, None), 1.0 / 2.4) - 0.055,
    )
    return clamp_array(compressed * 255.0, 0, 255)


_RGB_TO_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041],
], dtype=np.float64)

_XYZ_TO_RGB = np.linalg.inv(_RGB_TO_XYZ)


def _f_lab(t: np.ndarray) -> np.ndarray:
    delta = 6.0 / 29.0
    return np.where(t > delta ** 3, np.cbrt(t), t / (3 * delta ** 2) + 4.0 / 29.0)


def _f_lab_inv(t: np.ndarray) -> np.ndarray:
    delta = 6.0 / 29.0
    return np.where(t > delta, t ** 3, 3 * delta ** 2 * (t - 4.0 / 29.0))


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """Convert (H, W, 3) uint8 RGB → float64 CIE L*a*b*."""
    lin = _gamma_expand_srgb(rgb.astype(np.float64))
    xyz = lin @ _RGB_TO_XYZ.T
    xyz_n = xyz / _D65_WHITE
    f = _f_lab(xyz_n)
    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
    """Convert float64 L*a*b* → uint8 RGB."""
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    fy = (L + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0
    xyz = np.stack([_f_lab_inv(fx), _f_lab_inv(fy), _f_lab_inv(fz)], axis=-1)
    xyz = xyz * _D65_WHITE
    lin = xyz @ _XYZ_TO_RGB.T
    return _gamma_compress_srgb(lin).astype(np.uint8)


# ---------------------------------------------------------------------------
# Convolution / kernel operations (from scratch, no scipy)
# ---------------------------------------------------------------------------

def gaussian_kernel_1d(sigma: float, radius: int) -> np.ndarray:
    """Return a normalised 1-D Gaussian kernel of length 2*radius+1."""
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    k = np.exp(-0.5 * (x / sigma) ** 2)
    return k / k.sum()


def convolve_1d_horizontal(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Apply a 1-D kernel along the horizontal (column) axis of an (H, W, C) array."""
    r = len(kernel) // 2
    H, W, C = img.shape
    padded = np.pad(img.astype(np.float64), ((0, 0), (r, r), (0, 0)), mode='reflect')
    out = np.zeros_like(img, dtype=np.float64)
    for i, k in enumerate(kernel):
        out += padded[:, i:i + W, :] * k
    return out


def convolve_1d_vertical(img: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Apply a 1-D kernel along the vertical (row) axis of an (H, W, C) array."""
    r = len(kernel) // 2
    H, W, C = img.shape
    padded = np.pad(img.astype(np.float64), ((r, r), (0, 0), (0, 0)), mode='reflect')
    out = np.zeros_like(img, dtype=np.float64)
    for i, k in enumerate(kernel):
        out += padded[i:i + H, :, :] * k
    return out


def gaussian_blur(img: np.ndarray, sigma: float = 1.5, radius: int = 3) -> np.ndarray:
    """
    Apply separable Gaussian blur to an (H, W, C) float64 or uint8 image.
    Returns float64.
    """
    k = gaussian_kernel_1d(sigma, radius)
    out = convolve_1d_horizontal(img.astype(np.float64), k)
    out = convolve_1d_vertical(out, k)
    return out


# ---------------------------------------------------------------------------
# Affine transform helpers
# ---------------------------------------------------------------------------

def make_scale_translate_matrix(sx: float, sy: float,
                                tx: float, ty: float) -> np.ndarray:
    """Return a 3×3 homogeneous affine matrix for scale + translate."""
    return np.array([
        [sx,  0,  tx],
        [ 0, sy,  ty],
        [ 0,  0,   1],
    ], dtype=np.float64)


def invert_affine(M: np.ndarray) -> np.ndarray:
    """Invert a 3×3 affine matrix."""
    return np.linalg.inv(M)


def bilinear_sample(img: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Bilinear sampling at fractional pixel positions.

    img : (H, W, C) float64
    x   : (N,) array of column indices (fractional)
    y   : (N,) array of row    indices (fractional)

    Returns (N, C) float64 sampled values.
    """
    H, W, C = img.shape
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    x1 = x0 + 1
    y1 = y0 + 1
    # Fractional parts
    fx = x - x0
    fy = y - y0
    # Clamp to valid range
    x0c = np.clip(x0, 0, W - 1)
    x1c = np.clip(x1, 0, W - 1)
    y0c = np.clip(y0, 0, H - 1)
    y1c = np.clip(y1, 0, H - 1)
    # Corner values
    I00 = img[y0c, x0c]  # (N, C)
    I10 = img[y0c, x1c]
    I01 = img[y1c, x0c]
    I11 = img[y1c, x1c]
    # Interpolate
    fx = fx[:, None]
    fy = fy[:, None]
    return (I00 * (1 - fx) * (1 - fy) +
            I10 * fx       * (1 - fy) +
            I01 * (1 - fx) * fy       +
            I11 * fx       * fy)


def warp_affine(src: np.ndarray, M: np.ndarray,
                out_size: Tuple[int, int]) -> np.ndarray:
    """
    Apply an affine transform to src and produce output of out_size (W, H).

    Uses inverse mapping + bilinear interpolation.
    src: (H, W, C) float64
    M  : 3×3 affine matrix (maps src→dst)
    Returns: (out_H, out_W, C) float64
    """
    out_W, out_H = out_size
    M_inv = invert_affine(M)
    # Build grid of destination pixel centres
    xs, ys = np.meshgrid(np.arange(out_W), np.arange(out_H))
    pts = np.stack([xs.ravel(), ys.ravel(), np.ones(out_W * out_H)], axis=1)  # (N, 3)
    src_pts = (M_inv @ pts.T).T  # (N, 3)
    src_x = src_pts[:, 0]
    src_y = src_pts[:, 1]
    sampled = bilinear_sample(src, src_x, src_y)  # (N, C)
    return sampled.reshape(out_H, out_W, src.shape[2])
