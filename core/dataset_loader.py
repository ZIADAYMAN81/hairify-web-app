import os
from core.image_loader import load_image

def load_dataset(root_folder):
    """
    Loads labeled images from subfolders representing classes.
    Returns:
      dataset: list of (pixel_matrix, class_index) tuples
      class_names: list of string names for classes
    """
    dataset = []
    class_names = []
    
    if not os.path.exists(root_folder):
        print(f"Dataset folder '{root_folder}' not found.")
        return dataset, class_names
        
    for item in sorted(os.listdir(root_folder)):
        folder_path = os.path.join(root_folder, item)
        if os.path.isdir(folder_path):
            class_idx = len(class_names)
            class_names.append(item)
            
            for file in sorted(os.listdir(folder_path)):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(folder_path, file)
                    matrix = load_image(img_path)
                    dataset.append((matrix, class_idx))
                    
    print(f"Loaded {len(dataset)} images across {len(class_names)} classes: {class_names}")
    return dataset, class_names
