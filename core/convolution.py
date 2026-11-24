def convolve2d(channel, kernel):
    """
    Applies a 2D convolution to a single color channel (2D list) using a given kernel.
    Uses zero-padding to preserve original dimensions.
    """
    img_h = len(channel)
    img_w = len(channel[0]) if img_h > 0 else 0
    
    kh = len(kernel)
    kw = len(kernel[0]) if kh > 0 else 0
    
    pad_h = kh // 2
    pad_w = kw // 2
    
    # Create padded channel with zeros
    padded = []
    for y in range(img_h + 2 * pad_h):
        row = []
        for x in range(img_w + 2 * pad_w):
            if y < pad_h or y >= img_h + pad_h or x < pad_w or x >= img_w + pad_w:
                row.append(0)
            else:
                row.append(channel[y - pad_h][x - pad_w])
        padded.append(row)
        
    output = []
    for y in range(img_h):
        out_row = []
        for x in range(img_w):
            val = 0
            for ky in range(kh):
                for kx in range(kw):
                    val += padded[y + ky][x + kx] * kernel[ky][kx]
            out_row.append(val)
        output.append(out_row)
        
    return output
