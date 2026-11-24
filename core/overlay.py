import numpy as np
from PIL import Image

def load_rgba_image(path):
    """
    Helper to load an RGBA image as a NumPy array.
    """
    img = Image.open(path).convert('RGBA')
    return np.array(img)

def overlay_hairstyle(base_array, hairstyle_array, alpha=0.8):
    """
    Overlays a hairstyle array (RGBA) onto a base array (RGB) using NumPy.
    """
    base_h, base_w, _ = base_array.shape
    hair_h, hair_w, _ = hairstyle_array.shape
    
    # Calculate offset to top-center
    offset_x = (base_w - hair_w) // 2
    offset_y = 0
    
    # Create result array
    result = base_array.copy()
    
    # Determine overlap region
    y1, y2 = max(0, offset_y), min(base_h, offset_y + hair_h)
    x1, x2 = max(0, offset_x), min(base_w, offset_x + hair_w)
    
    hy1, hy2 = max(0, -offset_y), min(hair_h, base_h - offset_y)
    hx1, hx2 = max(0, -offset_x), min(hair_w, base_w - offset_x)
    
    if y1 >= y2 or x1 >= x2:
        return result

    # Extract regions
    hair_region = hairstyle_array[hy1:hy2, hx1:hx2]
    
    # Alpha blending using NumPy vectorized operations
    # hair_region is (H, W, 4) -> R, G, B, A
    hair_rgb = hair_region[:, :, :3]
    hair_alpha = (hair_region[:, :, 3] / 255.0) * alpha
    hair_alpha = np.expand_dims(hair_alpha, axis=-1) # (H, W, 1)
    
    bg_region = result[y1:y2, x1:x2]
    
    # Blending formula: out = alpha * fg + (1 - alpha) * bg
    blended = (hair_alpha * hair_rgb + (1 - hair_alpha) * bg_region).astype(np.uint8)
    
    result[y1:y2, x1:x2] = blended
    return result

def remove_hair(image_array, face_x, face_y, face_w, face_h):
    """
    Simulates hair removal by blurring the area above the forehead 
    to create a 'clean' base for the new hairstyle.
    """
    h, w, _ = image_array.shape
    result = image_array.copy()
    
    # Define the 'hair zone' (above the face box and slightly to the sides)
    hair_y_start = max(0, face_y - int(face_h * 0.4))
    hair_y_end = face_y + int(face_h * 0.2)
    hair_x_start = max(0, face_x - int(face_w * 0.2))
    hair_x_end = min(w, face_x + face_w + int(face_w * 0.2))
    
    # Extract and blur the zone
    # We use a simple box blur with NumPy
    zone = result[hair_y_start:hair_y_end, hair_x_start:hair_x_end]
    if zone.size > 0:
        # Simple pixelation/blur by downsampling and upsampling
        small = Image.fromarray(zone).resize((10, 10))
        blurred_zone = np.array(small.resize((zone.shape[1], zone.shape[0]), Image.Resampling.BILINEAR))
        result[hair_y_start:hair_y_end, hair_x_start:hair_x_end] = blurred_zone
        
    return result
