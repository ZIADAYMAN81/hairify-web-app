import numpy as np
from dataclasses import dataclass
from utils.math_utils import rgb_to_ycbcr

@dataclass
class FaceResult:
    found: bool
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0
    cx: float = 0.0
    cy: float = 0.0
    confidence: float = 0.0

def _skin_mask_ycbcr(rgb: np.ndarray) -> np.ndarray:
    """Boolean mask of skin-tone pixels using standard YCbCr thresholds."""
    ycbcr = rgb_to_ycbcr(rgb)
    Cb = ycbcr[:, :, 1]
    Cr = ycbcr[:, :, 2]
    return (Cb >= 77) & (Cb <= 127) & (Cr >= 133) & (Cr <= 173)

def detect_face(image_rgba: np.ndarray) -> FaceResult:
    """
    Detects the main face area using a high-speed vectorized skin-tone mask.
    """
    H, W = image_rgba.shape[:2]
    mask = _skin_mask_ycbcr(image_rgba[:, :, :3])
    
    # Find the bounding box of the largest skin-tone cluster
    coords = np.argwhere(mask)
    
    if coords.size < (W * H * 0.01): # If less than 1% of image is skin, fail
        return _fallback(W, H)
        
    # Get bounding box
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    
    bw, bh = x1 - x0, y1 - y0
    
    # Validate aspect ratio (faces aren't usually extremely wide or thin)
    aspect = bw / max(bh, 1)
    if aspect < 0.2 or aspect > 3.0:
        return _fallback(W, H)

    return FaceResult(
        found=True,
        x=int(x0), y=int(y0), w=int(bw), h=int(bh),
        cx=float(x0 + bw / 2),
        cy=float(y0 + bh / 2),
        confidence=float(coords.size / (W * H))
    )

def _fallback(img_w: int, img_h: int) -> FaceResult:
    """Centred fallback when detection fails."""
    w = img_w // 2
    h = int(img_h * 0.6)
    x = (img_w - w) // 2
    y = int(img_h * 0.05)
    return FaceResult(found=False, x=x, y=y, w=w, h=h, cx=x+w/2, cy=y+h/2)
