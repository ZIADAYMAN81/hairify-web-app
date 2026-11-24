"""
app.py — Main Hairify application class.

Wires together: GUI panels ↔ core engine ↔ hairstyle catalog.

State management:
  - _base_image : original RGBA array (full res)
  - _result     : composited RGBA array (full res)
  - _style      : currently selected HairstyleBase
  - _landmarks  : LandmarkResult from the last detection
  - _undo_stack : list of (overlay_arr, offset_x, offset_y) states
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import copy
import numpy as np
from typing import Optional, List

from gui import theme as T
from gui.panels import ControlPanel, PreviewPanel, GalleryPanel
from gui.widgets import StatusBar

from core.image_utils import load_image, save_image, image_size
from core.face_detector import detect_face
from core.landmark_finder import find_landmarks
from core.hair_renderer import render_hair, make_split_view
from core.color_transfer import transfer_hair_color, adjust_opacity

from hairstyles.style_catalog import ALL_STYLES
from hairstyles.base_style import HairstyleBase


MAX_UNDO = 10
OVERLAY_CANVAS_SIZE = 512   # size at which overlays are generated


class HairifyApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("✂ Hairify — Hairstyle Simulator")
        self.configure(bg=T.BG_DARKEST)
        self.minsize(T.MIN_W, T.MIN_H)
        self.geometry(f"{T.MIN_W}x{T.MIN_H}")

        # ---- State ----
        self._base_image: Optional[np.ndarray] = None    # (H, W, 4) RGBA
        self._result:     Optional[np.ndarray] = None
        self._style:      Optional[HairstyleBase] = None
        self._overlay_raw: Optional[np.ndarray] = None   # generated at canvas size
        self._landmarks   = None
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._undo_stack: List[dict] = []
        self._redo_stack: List[dict] = []
        self._processing = False

        self._build_ui()
        self._gallery.populate(ALL_STYLES)

    # -----------------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------------

    def _build_ui(self):
        # Menu bar
        menubar = tk.Menu(self, bg=T.BG_DARK, fg=T.TEXT_PRIMARY,
                          activebackground=T.ACCENT_PRIMARY)
        file_menu = tk.Menu(menubar, tearoff=0, bg=T.BG_CARD,
                            fg=T.TEXT_PRIMARY,
                            activebackground=T.ACCENT_PRIMARY)
        file_menu.add_command(label="Open Photo…", command=self.upload_photo)
        file_menu.add_command(label="Export PNG…", command=self.export_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0, bg=T.BG_CARD,
                            fg=T.TEXT_PRIMARY,
                            activebackground=T.ACCENT_PRIMARY)
        edit_menu.add_command(label="Undo", command=self.undo,
                              accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo,
                              accelerator="Ctrl+Y")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        self.config(menu=menubar)

        # Keyboard shortcuts
        self.bind_all("<Control-z>", lambda e: self.undo())
        self.bind_all("<Control-y>", lambda e: self.redo())
        self.bind_all("<Control-o>", lambda e: self.upload_photo())
        self.bind_all("<Control-s>", lambda e: self.export_image())

        # ---- Three-column layout ----
        main = tk.Frame(self, bg=T.BG_DARKEST)
        main.pack(fill="both", expand=True)

        self._control = ControlPanel(main, app=self)
        self._control.pack(side="left", fill="y")

        # Thin separator
        tk.Frame(main, bg=T.BORDER_COLOR, width=1).pack(side="left", fill="y")

        self._preview = PreviewPanel(main, app=self)
        self._preview.pack(side="left", fill="both", expand=True)

        tk.Frame(main, bg=T.BORDER_COLOR, width=1).pack(side="left", fill="y")

        self._gallery = GalleryPanel(main, app=self)
        self._gallery.pack(side="left", fill="y")

        # Status bar
        self._status = StatusBar(self)
        self._status.pack(side="bottom", fill="x")

    # -----------------------------------------------------------------------
    # Photo upload
    # -----------------------------------------------------------------------

    def upload_photo(self):
        path = filedialog.askopenfilename(
            title="Select a photo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp *.tiff"),
                       ("All files", "*.*")]
        )
        if not path:
            return

        self._status.set("Loading photo…", T.TEXT_ACCENT)
        self.update_idletasks()

        try:
            img = load_image(path)
        except Exception as ex:
            messagebox.showerror("Load Error", f"Cannot open image:\n{ex}")
            self._status.set("Error loading photo", T.ERROR)
            return

        # Downsample very large images for performance
        H, W = img.shape[:2]
        max_dim = 1200
        if max(H, W) > max_dim:
            scale = max_dim / max(H, W)
            new_w, new_h = int(W * scale), int(H * scale)
            from core.image_utils import resize_array
            img = resize_array(img, new_w, new_h)

        self._base_image = img
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._undo_stack.clear()
        self._redo_stack.clear()

        # Run face detection in background thread
        self._status.set("Detecting face…", T.TEXT_ACCENT)
        self.update_idletasks()
        threading.Thread(target=self._detect_and_render, daemon=True).start()

    def _detect_and_render(self):
        img = self._base_image
        face = detect_face(img)
        self._landmarks = find_landmarks(face.x, face.y, face.w, face.h)

        status_text = (
            f"Face detected (confidence {face.confidence:.0%})"
            if face.found else
            "No face detected — using fallback placement. Drag to adjust."
        )
        color = T.SUCCESS if face.found else T.WARNING
        conf = face.confidence if face.found else 0.3

        self.after(0, lambda: self._control.update_detection(
            face.found, conf, status_text))
        self.after(0, lambda: self._status.set(status_text, color))
        self.after(0, self._render)

    # -----------------------------------------------------------------------
    # Rendering pipeline
    # -----------------------------------------------------------------------

    def _render(self):
        if self._base_image is None:
            return
        if self._processing:
            return
        self._processing = True
        threading.Thread(target=self._render_thread, daemon=True).start()

    def _render_thread(self):
        try:
            base = self._base_image
            H, W = base.shape[:2]

            if self._style is None or self._landmarks is None:
                # Show base image
                self.after(0, lambda: self._preview.show_image(base))
                self._result = base.copy()
                return

            # Generate overlay at full image size resolution
            ov_raw = self._style.generate_overlay(OVERLAY_CANVAS_SIZE, OVERLAY_CANVAS_SIZE)

            # Apply color transfer
            color = self._control.get_color()
            ov_colored = transfer_hair_color(ov_raw, color, strength=0.9)

            # Apply opacity
            opacity = self._control.get_opacity()
            ov_colored = adjust_opacity(ov_colored, opacity)

            # Composite
            result = render_hair(
                base=base,
                overlay=ov_colored,
                landmarks=self._landmarks,
                offset_x=self._offset_x,
                offset_y=self._offset_y,
                scale=self._control.get_scale(),
                feather_sigma=self._control.get_feather(),
                shadow=self._control.get_shadow(),
            )

            # Split view
            if self._control.get_split():
                result = make_split_view(base, result)

            self._result = result
            self.after(0, lambda: self._preview.show_image(result))
            self.after(0, lambda: self._status.set(
                f"Style: {self._style.name}  |  Drag overlay to reposition",
                T.TEXT_ACCENT))
        except Exception as ex:
            self.after(0, lambda: self._status.set(f"Render error: {ex}", T.ERROR))
        finally:
            self._processing = False

    # -----------------------------------------------------------------------
    # Control callbacks
    # -----------------------------------------------------------------------

    def on_style_selected(self, style: HairstyleBase):
        self._push_undo()
        self._style = style
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._status.set(f"Selected: {style.name}", T.TEXT_ACCENT)
        # Set default color in picker
        self._control._color_picker.set(style.default_color)
        self._render()

    def on_color_changed(self, rgb):
        self._render()

    def on_opacity_changed(self, v):
        self._render()

    def on_scale_changed(self, v):
        self._render()

    def on_feather_changed(self, v):
        self._render()

    def on_shadow_changed(self):
        self._render()

    def on_split_changed(self):
        self._render()

    def nudge_overlay(self, dx: float, dy: float):
        self._offset_x += dx
        self._offset_y += dy
        self._render()

    # -----------------------------------------------------------------------
    # Undo / Redo
    # -----------------------------------------------------------------------

    def _current_state(self) -> dict:
        return {
            "style": self._style,
            "offset_x": self._offset_x,
            "offset_y": self._offset_y,
        }

    def _restore_state(self, state: dict):
        self._style = state["style"]
        self._offset_x = state["offset_x"]
        self._offset_y = state["offset_y"]

    def _push_undo(self):
        self._undo_stack.append(self._current_state())
        if len(self._undo_stack) > MAX_UNDO:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            self._status.set("Nothing to undo", T.TEXT_MUTED)
            return
        self._redo_stack.append(self._current_state())
        state = self._undo_stack.pop()
        self._restore_state(state)
        self._render()

    def redo(self):
        if not self._redo_stack:
            self._status.set("Nothing to redo", T.TEXT_MUTED)
            return
        self._undo_stack.append(self._current_state())
        state = self._redo_stack.pop()
        self._restore_state(state)
        self._render()

    # -----------------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------------

    def export_image(self):
        if self._result is None:
            messagebox.showwarning("Export", "Nothing to export yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All files", "*.*")],
            title="Save result as…"
        )
        if not path:
            return
        try:
            save_image(self._result, path)
            self._status.set(f"Exported → {path}", T.SUCCESS)
        except Exception as ex:
            messagebox.showerror("Export Error", str(ex))
