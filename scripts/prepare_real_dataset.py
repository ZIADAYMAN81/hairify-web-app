import os
import sys
import random
import csv
from PIL import Image

def process_dataset(source_dir):
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' not found.")
        return

    output_base = os.path.join("data", "dataset")
    classes = ["curly", "straight", "wavy", "coily"]
    
    # Create empty output directories
    for cls in classes:
        cls_path = os.path.join(output_base, cls)
        os.makedirs(cls_path, exist_ok=True)
        # Clear existing contents if any
        for f in os.listdir(cls_path):
            os.remove(os.path.join(cls_path, f))
            
    class_files = {cls: [] for cls in classes}
    csv_files = [f for f in os.listdir(source_dir) if f.endswith('.csv')]
    
    if csv_files:
        print(f"Found CSV label file: {csv_files[0]}. Parsing...")
        with open(os.path.join(source_dir, csv_files[0]), 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if len(row) >= 2:
                    filename = row[0].strip()
                    label = row[1].strip().lower()
                    if label in classes:
                        class_files[label].append(os.path.join(source_dir, filename))
    else:
        print("No CSV found. Assuming subfolder structure...")
        folder_mapping = {
            "Curly": "curly",
            "Straight": "straight",
            "Wavy": "wavy",
            "Kinky": "coily"
        }
        for raw_folder, cls in folder_mapping.items():
            cls_dir = os.path.join(source_dir, raw_folder)
            if os.path.isdir(cls_dir):
                for f in os.listdir(cls_dir):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        class_files[cls].append(os.path.join(cls_dir, f))
                        
    # Print before balancing
    print("\n--- Found Images Before Balancing ---")
    for cls in classes:
        print(f"{cls}: {len(class_files[cls])} images")
        
    # Balance dataset
    # Find minimum class count among non-empty classes
    counts = [len(files) for files in class_files.values() if files]
    if not counts:
        print("No valid images found for any class.")
        return
        
    min_count = min(counts)
    
    if min_count > 0:
        print(f"\nBalancing all available classes to {min_count} images...")
        for cls in classes:
            if len(class_files[cls]) > min_count:
                class_files[cls] = random.sample(class_files[cls], min_count)
                
    # Process images
    print("\n--- Processing Images ---")
    total_processed = 0
    skipped_count = 0
    
    for cls in classes:
        successful = 0
        for i, filepath in enumerate(class_files[cls]):
            try:
                if not os.path.exists(filepath):
                    continue
                with Image.open(filepath) as img:
                    img = img.convert('RGB')
                    img = img.resize((64, 64))
                    out_name = f"{cls}_{i:04d}.png"
                    out_path = os.path.join(output_base, cls, out_name)
                    img.save(out_path, format="PNG")
                    successful += 1
                    total_processed += 1
            except Exception as e:
                print(f"Skipped {filepath}: Corrupted or unreadable ({e})")
                skipped_count += 1
                
        print(f"{cls}: {successful} images saved.")
        
    print("\n--- Final Report ---")
    print(f"Total processed: {total_processed}")
    print(f"Total skipped: {skipped_count}")

if __name__ == "__main__":
    source_path = r"D:\archive\data"
    if len(sys.argv) >= 2:
        source_path = sys.argv[1]
    process_dataset(source_path)
