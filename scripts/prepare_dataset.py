import os
from PIL import Image

def prepare_dataset(dataset_dir="data/dataset"):
    print(f"Preparing dataset in: {dataset_dir}")
    
    if not os.path.exists(dataset_dir):
        print(f"Error: Directory '{dataset_dir}' does not exist.")
        return
        
    total_processed = 0
    
    # Loop through each subfolder (class)
    for class_name in sorted(os.listdir(dataset_dir)):
        class_dir = os.path.join(dataset_dir, class_name)
        
        if not os.path.isdir(class_dir):
            continue
            
        class_count = 0
        
        # Loop through each image in the class folder
        for file_name in os.listdir(class_dir):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                file_path = os.path.join(class_dir, file_name)
                
                try:
                    # Open, convert to RGB, and resize to 64x64
                    with Image.open(file_path) as img:
                        img = img.convert('RGB')
                        img = img.resize((64, 64))
                        # Save in place, overwriting the original
                        img.save(file_path)
                    
                    class_count += 1
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")
                    
        print(f"Class '{class_name}': Processed {class_count} images.")
        total_processed += class_count
        
    print(f"Dataset preparation complete. Total images processed: {total_processed}")

if __name__ == "__main__":
    prepare_dataset()
