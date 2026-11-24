import math
from core.convolution import convolve2d

def sobel_edges(image_matrix):
    """
    Applies the Sobel operator to compute edge magnitude.
    Returns a 2D list representing edge magnitudes (0-255).
    """
    h = len(image_matrix)
    w = len(image_matrix[0]) if h > 0 else 0
    
    # Convert to grayscale manually
    gray = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = image_matrix[y][x]
            intensity = 0.299 * r + 0.587 * g + 0.114 * b
            row.append(intensity)
        gray.append(row)
        
    # Sobel kernels
    Gx = [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ]
    Gy = [
        [-1, -2, -1],
        [ 0,  0,  0],
        [ 1,  2,  1]
    ]
    
    grad_x = convolve2d(gray, Gx)
    grad_y = convolve2d(gray, Gy)
    
    magnitude = []
    max_val = 0
    
    # Compute magnitude
    for y in range(h):
        row = []
        for x in range(w):
            val = math.sqrt(grad_x[y][x]**2 + grad_y[y][x]**2)
            if val > max_val:
                max_val = val
            row.append(val)
        magnitude.append(row)
        
    # Normalize to 0-255
    if max_val > 0:
        for y in range(h):
            for x in range(w):
                magnitude[y][x] = int((magnitude[y][x] / max_val) * 255)
                
    return magnitude
