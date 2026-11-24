def threshold_segment(image_matrix, threshold=128):
    """
    Converts image to grayscale manually and applies a binary threshold.
    Returns a 2D mask where foreground=255, background=0.
    """
    h = len(image_matrix)
    w = len(image_matrix[0]) if h > 0 else 0
    
    mask = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = image_matrix[y][x]
            gray = 0.299 * r + 0.587 * g + 0.114 * b
            if gray >= threshold:
                row.append(255)
            else:
                row.append(0)
        mask.append(row)
        
    return mask
