import numpy as np
from PIL import Image

def load_image(path):
    """
    Loads an image from the given path and returns it as a NumPy array (H, W, 3).
    """
    img = Image.open(path).convert('RGB')
    pixel_array = np.array(img)
    return pixel_array

def save_image(array, path):
    """
    Saves a NumPy array (H, W, 3) to the given path as an image.
    """
    # Ensure array is in uint8 format for PIL
    array = np.clip(array, 0, 255).astype(np.uint8)
    img = Image.fromarray(array)
    img.save(path)
    print(f"Saved image to '{path}' with dimensions: {img.width}x{img.height}")
