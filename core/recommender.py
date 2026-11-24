def get_face_shape(w, h):
    """
    Determines face shape based on bounding box aspect ratio.
    """
    ratio = h / w if w > 0 else 1.0
    
    if ratio < 1.15:
        return "round"
    elif ratio < 1.35:
        return "square"
    elif ratio < 1.55:
        return "oval"
    else:
        return "long"

def recommend_style(face_shape, detected_hair_type):
    """
    Recommends a hairstyle based on the intersection of 
    detected face shape and existing hair texture.
    """
    # Professional styling logic:
    # 1. Round faces benefit from vertical lines (Straight)
    # 2. Square faces benefit from softening (Curly)
    # 3. Oval faces benefit from balanced volume (Wavy)
    # 4. Long faces benefit from horizontal width (Coily)
    
    logic = {
        "round": "straight",
        "square": "curly",
        "oval": "wavy",
        "long": "coily"
    }
    
    recommended = logic.get(face_shape, "straight")
    
    # If the recommendation is the same as current, suggest a slight variation
    # (In a real app, we might suggest different colors or lengths)
    
    return recommended
