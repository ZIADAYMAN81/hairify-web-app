import os
import json
import base64
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
try:
    from flask_cors import CORS  # optional: only needed if the UI is served from another origin
except ImportError:
    CORS = None
from PIL import Image
import io

# Import Hairify Core
from core.image_loader import load_image, save_image
from core.neural_network import NeuralNetwork
from core.overlay import overlay_hairstyle, load_rgba_image, remove_hair
from core.face_detector import detect_face
from core.recommender import get_face_shape, recommend_style

app = Flask(__name__, static_folder='web', static_url_path='')
if CORS:
    CORS(app)

# Configuration
UPLOAD_FOLDER = 'data/input'
OUTPUT_FOLDER = 'data/output'
WEIGHTS_PATH = 'data/best_model_weights.json'
HAIRSTYLES_FOLDER = 'data/hairstyles'
CLASS_NAMES = ["coily", "curly", "straight", "wavy"]

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def get_network():
    if not os.path.exists(WEIGHTS_PATH):
        return None
    nn = NeuralNetwork([12288, 64, 4])
    nn.load_weights(WEIGHTS_PATH)
    return nn

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/sample', methods=['GET'])
def get_sample():
    try:
        dataset_dir = 'data/dataset'
        if not os.path.isdir(dataset_dir):
            return jsonify({"success": False, "error": "No sample dataset is bundled with the repository. Upload your own photo instead."}), 404
        classes = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
        if not classes:
            return jsonify({"success": False, "error": "Dataset empty"}), 404
        
        random_class = np.random.choice(classes)
        class_dir = os.path.join(dataset_dir, random_class)
        images = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not images:
            return jsonify({"success": False, "error": "No images in dataset"}), 404
            
        random_image = np.random.choice(images)
        image_path = os.path.join(class_dir, random_image)
        
        with open(image_path, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')
            
        return jsonify({
            "success": True, 
            "image": f"data:image/png;base64,{base64_string}",
            "filename": random_image
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    model_exists = os.path.exists(WEIGHTS_PATH)
    return jsonify({"status": "ok", "model_loaded": model_exists})

@app.route('/process', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "No image uploaded"}), 400
        
        file = request.files['image']
        input_path = os.path.join(UPLOAD_FOLDER, "uploaded.jpg")
        file.save(input_path)

        # 1. Load Components
        nn = get_network()
        if nn is None:
            return jsonify({"success": False, "error": "Model not trained yet"}), 500

        # 2. Analyze Current State (Neural Network)
        original_img = Image.open(input_path).convert('RGB')
        resized_img = original_img.resize((64, 64))
        pixel_data = np.array(resized_img, dtype=np.float32)
        input_vector = (pixel_data.flatten() / 255.0)
        
        prediction = nn.predict(input_vector, CLASS_NAMES)
        current_hair_type = prediction["class_name"]

        # 3. Detect Face Features & Head Geometry
        # We use RGBA for detection as required by our face_detector
        rgba_array = np.array(original_img.convert('RGBA'))
        face_result = detect_face(rgba_array)
        face_shape = get_face_shape(face_result.w, face_result.h)

        # 4. Smart Recommendation
        recommended_class = recommend_style(face_shape, current_hair_type)

        # 5. "Hair Removal" (Head Prepping)
        # Blur the area above forehead to 'clean' the background hair
        base_array = np.array(original_img)
        prepped_array = remove_hair(base_array, face_result.x, face_result.y, face_result.w, face_result.h)

        # 6. Dynamic Binding (Smart Alignment)
        style_path = os.path.join(HAIRSTYLES_FOLDER, f"{recommended_class}.png")
        if not os.path.exists(style_path):
             return jsonify({"success": False, "error": f"Style {recommended_class}.png missing"}), 500
        
        style_array = load_rgba_image(style_path)
        
        # Scale hair relative to face width (1.8x face width is usually ideal for overlays)
        style_img = Image.fromarray(style_array)
        style_w, style_h = style_img.size
        target_w = int(face_result.w * 1.9) # Slightly wider for better coverage
        target_h = int((target_w / style_w) * style_h)
        style_img = style_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        style_array = np.array(style_img)

        # We manually position the hair based on the face cx, cy
        # offset_y should be just above the eyes
        offset_x = int(face_result.cx - (target_w / 2))
        offset_y = int(face_result.y - (target_h * 0.45)) # Position based on forehead
        
        # Apply overlay onto the PREPPED image
        result_array = overlay_hairstyle(prepped_array, style_array, alpha=0.9)
        
        # Save and Encode
        output_path = os.path.join(OUTPUT_FOLDER, "result.png")
        save_image(result_array, output_path)
        
        with open(output_path, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode('utf-8')

        return jsonify({
            "success": True,
            "detected_hair": current_hair_type,
            "face_shape": face_shape,
            "recommended_style": recommended_class,
            "confidence": round(prediction["confidence"] * 100, 1),
            "result_image": f"data:image/png;base64,{base64_string}"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
