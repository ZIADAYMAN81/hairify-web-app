import os
from core.image_loader import load_image, save_image
from core.overlay import overlay_hairstyle, load_rgba_image

def main():
    face_path = os.path.join("data", "input", "test_face.jpg")
    hairstyles_dir = os.path.join("data", "hairstyles")
    output_dir = os.path.join("data", "output")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(face_path):
        print(f"Error: Face image not found at {face_path}")
        print("Please place a test_face.jpg file in data/input/ before running.")
        return
        
    print(f"Loading base face: {face_path}")
    base_matrix = load_image(face_path)
    
    styles = ["curly", "straight", "wavy", "coily"]
    
    for style in styles:
        hair_path = os.path.join(hairstyles_dir, f"{style}.png")
        if not os.path.exists(hair_path):
            print(f"Warning: Hairstyle overlay {hair_path} not found. Skipping {style}.")
            continue
            
        print(f"Applying {style} overlay...")
        hair_matrix = load_rgba_image(hair_path)
        result_matrix = overlay_hairstyle(base_matrix, hair_matrix, alpha=0.85)
        
        out_path = os.path.join(output_dir, f"result_{style}.png")
        save_image(result_matrix, out_path)
        print(f"Saved: {out_path}")
        
    print("Overlay test complete — check data/output/")

if __name__ == "__main__":
    main()
