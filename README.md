# Hairify Web App: Hairstyle Recommendation with a Physics-Driven UI

> Companion web app to my graduation project [Hairify](https://github.com/ZIADAYMAN81/hairify), The British University in Egypt, 2026. Author: Ziad Ayman.

A browser front-end built with **HTML, CSS and JavaScript** and a **Flask** API. Upload a photo; the back-end detects the face, classifies the current hair texture with a neural network written from scratch in NumPy, recommends a style for the detected face shape, and returns the photo with the new hairstyle overlaid.

## Front-end (`web/`)
- **Physics-driven layout.** On load, every UI element (logo, buttons, result panel) is a [Matter.js](https://brm.io/matter-js/) rigid body that falls and bounces under gravity. After four seconds the elements animate into a clean, centred layout.
- **Interaction.** File upload with preview, a processing spinner, and a results overlay that shows the detected hair type, face shape, recommended style and the rendered image. Talks to the API with `fetch` and `FormData`.
- **Styling.** A dark, glassmorphism theme in plain CSS (backdrop blur, gradients, transitions). No front-end framework.

## Back-end
| Module | What it does |
|---|---|
| `server.py` | Flask API: serves the UI, `POST /process` (full pipeline), `GET /health`, `GET /sample` |
| `core/neural_network.py`, `core/trainer.py` | Fully connected network (12,288 → 64 → 4) with forward pass, backpropagation and training loop written in NumPy, no ML framework |
| `core/face_detector.py` | Vectorised YCbCr skin-tone mask → face bounding box, with a safe fallback |
| `core/recommender.py` | Face shape from box proportions → recommended hair texture |
| `core/convolution.py`, `core/edge_detection.py`, `core/segmentation.py` | 2-D convolution, Sobel edges and threshold segmentation from first principles |
| `hairstyles/` | 10 procedurally drawn hairstyles (bob, pixie, afro, man bun, mohawk, …) rendered as RGBA overlays |
| `core/overlay.py`, `core/hair_renderer.py` | Alpha blending, hair-region clean-up and positioning relative to the face |
| `gui/` | Optional Tkinter desktop front-end for the same engine |

**Model:** the from-scratch network classifies 4 hair textures (coily, curly, straight, wavy). It reached **46.6% validation accuracy** after 100 epochs on 868 images (chance is 25%). This app is an engineering exercise in building the pipeline by hand. The production classifier for Hairify is the fine-tuned EfficientNet-B3 in the [main repository](https://github.com/ZIADAYMAN81/hairify).

## Run it
```bash
pip install -r requirements.txt
python tools/generate_overlays.py   # (re)renders data/hairstyles/*.png from the procedural styles
python server.py                    # then open http://localhost:5000
```
The trained weights (`data/best_model_weights.json`) are included. To retrain on your own labelled folders in `data/dataset/<class>/`, run `python main.py --train`.

## Tests
```bash
python -m pytest -q tests    # 17 tests: face detection, geometry helpers, hair rendering
```

## Notes
- No sample photos are bundled (privacy), so the **Example** button reports that and asks you to upload your own photo.
- Face detection is skin-tone based: fast and dependency-free, but less robust than a landmark model under unusual lighting.

## Tech stack
HTML5 · CSS3 · JavaScript (ES6, Fetch API) · Matter.js · Python · Flask · NumPy · Pillow · pytest
