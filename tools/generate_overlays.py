"""Render the four hair-texture overlay PNGs used by server.py (/process)
from the procedural hairstyle catalog. Run from the project root:

    python tools/generate_overlays.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image
from hairstyles.style_catalog import CATALOG

# Hair-texture class predicted by the network -> procedural style used as its overlay
MAPPING = {
    "straight": "Long Straight",
    "wavy": "Long Wavy",
    "curly": "Curly Afro",
    "coily": "Cornrows",
}

OUT_DIR = os.path.join("data", "hairstyles")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for cls, style_name in MAPPING.items():
        overlay = CATALOG[style_name].generate_overlay(400, 500)
        path = os.path.join(OUT_DIR, f"{cls}.png")
        Image.fromarray(overlay, "RGBA").save(path)
        print(f"wrote {path} ({style_name})")


if __name__ == "__main__":
    main()
