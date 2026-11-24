import os
import sys
from core.image_loader import load_image, save_image
from core.edge_detection import sobel_edges
from core.segmentation import threshold_segment
from core.overlay import overlay_hairstyle, load_rgba_image
from core.dataset_loader import load_dataset
from core.neural_network import NeuralNetwork
from core.trainer import train

def main():
    if '--train' in sys.argv:
        print("=== Hairify Training Mode ===")
        dataset_dir = 'data/dataset'
        dataset, class_names = load_dataset(dataset_dir)
        
        if not dataset:
            print("No dataset found to train on.")
            return
            
        print(f"Training on {len(dataset)} images across {len(class_names)} classes: {class_names}")
        
        input_size = 12288
        hidden_1 = 128
        hidden_2 = 64
        output_size = len(class_names)
        
        nn = NeuralNetwork([input_size, hidden_1, hidden_2, output_size])
        
        print(f"Starting training for 100 epochs...")
        nn = train(nn, dataset, epochs=100, learning_rate=0.01)
        
        if os.path.exists('data/best_model_weights.json'):
            print("Loading best weights for evaluation...")
            nn.load_weights('data/best_model_weights.json')
            
        print("\n--- Confusion Matrix ---")
        matrix = [[0] * output_size for _ in range(output_size)]
        
        import numpy as np
        for img_matrix, label in dataset:
            input_vector = (np.array(img_matrix, dtype=np.float32).flatten() / 255.0).tolist()
            pred = nn.predict(input_vector, class_names)
            matrix[label][pred["class_index"]] += 1
            
        header = f"{'':>12}" + "".join([f"{name[:8]:>10}" for name in class_names])
        print(header)
        for i, name in enumerate(class_names):
            row_str = f"{name[:8]:>12}"
            for j in range(output_size):
                row_str += f"{matrix[i][j]:>10}"
            print(row_str)
            
        return
    print("=== Hairify Pure Python Pipeline ===")
    
    # Ensure directories exist
    os.makedirs('data/input', exist_ok=True)
    os.makedirs('data/hairstyles', exist_ok=True)
    os.makedirs('data/output', exist_ok=True)
    
    input_path = 'data/input/user.png'
    hairstyle_path = 'data/hairstyles/style1.png'
    output_path = 'data/output/result.png'
    
    # For demonstration, creating dummy images if they don't exist
    if not os.path.exists(input_path):
        from PIL import Image
        img = Image.new('RGB', (200, 200), color=(200, 150, 150))
        img.save(input_path)
        print(f"Created dummy input at {input_path}")
        
    if not os.path.exists(hairstyle_path):
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (100, 100), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([10, 10, 90, 90], fill=(50, 20, 10, 255))
        img.save(hairstyle_path)
        print(f"Created dummy hairstyle at {hairstyle_path}")
        
    # 1. Load user image
    print("\n--- 1. Loading Image ---")
    base_matrix = load_image(input_path)
    
    # 2. Edge detection
    print("\n--- 2. Edge Detection ---")
    edges = sobel_edges(base_matrix)
    print("Edges detected. Matrix computed.")
    
    # 3. Segmentation
    print("\n--- 3. Segmentation ---")
    mask = threshold_segment(base_matrix, threshold=128)
    print("Segmentation done. Binary mask computed.")
    
    # 4. Overlay hairstyle
    print("\n--- 4. Overlay ---")
    hair_matrix = load_rgba_image(hairstyle_path)
    result_matrix = overlay_hairstyle(base_matrix, hair_matrix, alpha=0.8)
    
    # 5. Save result
    save_image(result_matrix, output_path)
    print("\nPipeline completed successfully! Result saved to data/output/result.png")

if __name__ == "__main__":
    main()
