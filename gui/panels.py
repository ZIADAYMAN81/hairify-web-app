"""
panels.py — The three main panels of the Hairify GUI.

  ControlPanel  — Left  : upload, detection info, adjustments
  PreviewPanel  — Centre: live canvas with before/after view + drag
  GalleryPanel  — Right : scrollable hairstyle thumbnail grid
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional
from PIL import Image, ImageTk

from gui import theme as T
from gui.widgets import (RoundedButton, ColorPicker, LabeledSlider,
                         SectionHeader, StatusBar)


# ---------------------------------------------------------------------------
# ControlPanel (left)
# ---------------------------------------------------------------------------

class ControlPanel(tk.Frame):

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=T.BG_DARK, width=T.LEFT_PANEL_W, **kwargs)
        self.pack_propagate(False)
        self.app = app
        self._build()

    def _build(self):
        # ---- Logo / title ----
        header = tk.Frame(self, bg=T.BG_DARK)
        header.pack(fill="x", padx=T.PAD, pady=(T.PAD_LG, T.PAD))

        tk.Label(header, text="✂ Hairify", bg=T.BG_DARK,
                 fg=T.ACCENT_PRIMARY, font=T.FONT_TITLE).pack(anchor="w")
        tk.Label(header, text="Hairstyle Simulator",
                 bg=T.BG_DARK, fg=T.TEXT_MUTED, font=T.FONT_SMALL).pack(anchor="w")

        tk.Frame(self, bg=T.BORDER_COLOR, height=1).pack(fill="x", pady=T.PAD_SM)

        # ---- Upload ----
        SectionHeader(self, "📷  Photo").pack(anchor="w", padx=T.PAD, pady=(T.PAD, 2))

        self._upload_btn = RoundedButton(
            self, text="Upload Photo", command=self.app.upload_photo,
            width=T.LEFT_PANEL_W - T.PAD * 2, height=40, icon="📂"
        )
        self._upload_btn.pack(padx=T.PAD, pady=4)

        # Detection status box
        self._det_frame = tk.Frame(self, bg=T.BG_CARD, padx=8, pady=6)
        self._det_frame.pack(fill="x", padx=T.PAD, pady=4)
        tk.Label(self._det_frame, text="Face Detection",
                 bg=T.BG_CARD, fg=T.TEXT_SECONDARY, font=T.FONT_SMALL).pack(anchor="w")
        self._det_status = tk.Label(self._det_frame, text="No photo loaded",
                                    bg=T.BG_CARD, fg=T.TEXT_MUTED,
                                    font=T.FONT_SMALL, wraplength=180, justify="left")
        self._det_status.pack(anchor="w")
        self._conf_bar_bg = tk.Canvas(self._det_frame, height=6,
                                      bg=T.BG_ELEVATED, highlightthickness=0)
        self._conf_bar_bg.pack(fill="x", pady=(4, 0))
        self._conf_bar = self._conf_bar_bg.create_rectangle(0, 0, 0, 6, fill=T.SUCCESS, width=0)

        tk.Frame(self, bg=T.BORDER_COLOR, height=1).pack(fill="x", pady=T.PAD_SM)

        # ---- Adjustments ----
        SectionHeader(self, "🎨  Adjustments").pack(anchor="w", padx=T.PAD, pady=(T.PAD, 2))

        self._color_picker = ColorPicker(
            self, label="Hair Color",
            initial=(50, 25, 10),
            on_change=self.app.on_color_changed
        )
        self._color_picker.pack(fill="x", padx=T.PAD, pady=4)

        self._opacity_slider = LabeledSlider(
            self, "Opacity", 0.1, 1.0, 1.0,
            on_change=self.app.on_opacity_changed
        )
        self._opacity_slider.pack(fill="x", padx=T.PAD, pady=2)

        self._scale_slider = LabeledSlider(
            self, "Hair Scale", 0.5, 2.0, 1.0,
            on_change=self.app.on_scale_changed
        )
        self._scale_slider.pack(fill="x", padx=T.PAD, pady=2)

        self._feather_slider = LabeledSlider(
            self, "Edge Softness", 0.5, 6.0, 2.0,
            on_change=self.app.on_feather_changed
        )
        self._feather_slider.pack(fill="x", padx=T.PAD, pady=2)

        tk.Frame(self, bg=T.BORDER_COLOR, height=1).pack(fill="x", pady=T.PAD_SM)

        # ---- Shadow toggle ----
        self._shadow_var = tk.BooleanVar(value=True)
        shadow_row = tk.Frame(self, bg=T.BG_DARK)
        shadow_row.pack(fill="x", padx=T.PAD, pady=4)
        tk.Label(shadow_row, text="Root Shadow",
                 bg=T.BG_DARK, fg=T.TEXT_SECONDARY,
                 font=T.FONT_LABEL).pack(side="left")
        tk.Checkbutton(shadow_row, variable=self._shadow_var,
                       bg=T.BG_DARK, fg=T.ACCENT_PRIMARY,
                       activebackground=T.BG_DARK,
                       selectcolor=T.BG_ELEVATED,
                       command=self.app.on_shadow_changed).pack(side="right")

        # ---- Split view toggle ----
        self._split_var = tk.BooleanVar(value=False)
        split_row = tk.Frame(self, bg=T.BG_DARK)
        split_row.pack(fill="x", padx=T.PAD, pady=4)
        tk.Label(split_row, text="Before/After Split",
                 bg=T.BG_DARK, fg=T.TEXT_SECONDARY,
                 font=T.FONT_LABEL).pack(side="left")
        tk.Checkbutton(split_row, variable=self._split_var,
                       bg=T.BG_DARK, fg=T.ACCENT_PRIMARY,
                       activebackground=T.BG_DARK,
                       selectcolor=T.BG_ELEVATED,
                       command=self.app.on_split_changed).pack(side="right")

        tk.Frame(self, bg=T.BORDER_COLOR, height=1).pack(fill="x", pady=T.PAD_SM)

        # ---- Undo/Redo / Export ----
        action_row = tk.Frame(self, bg=T.BG_DARK)
        action_row.pack(fill="x", padx=T.PAD, pady=4)

        RoundedButton(action_row, text="↩ Undo", command=self.app.undo,
                      width=80, height=32, bg=T.BG_ELEVATED,
                      bg_hover=T.BORDER_LIGHT).pack(side="left", padx=(0, 4))
        RoundedButton(action_row, text="↪ Redo", command=self.app.redo,
                      width=80, height=32, bg=T.BG_ELEVATED,
                      bg_hover=T.BORDER_LIGHT).pack(side="left")

        self._export_btn = RoundedButton(
            self, text="Export PNG", command=self.app.export_image,
            width=T.LEFT_PANEL_W - T.PAD * 2, height=40,
            bg=T.ACCENT_SECONDARY, bg_hover="#5fdede",
            fg=T.BG_DARKEST, icon="💾"
        )
        self._export_btn.pack(padx=T.PAD, pady=8)

    def update_detection(self, found: bool, confidence: float, text: str):
        color = T.SUCCESS if found else T.WARNING
        self._det_status.config(text=text, fg=color)
        w = self._conf_bar_bg.winfo_width()
        bar_w = int(w * confidence)
        self._conf_bar_bg.coords(self._conf_bar, 0, 0, bar_w, 6)
        self._conf_bar_bg.itemconfig(self._conf_bar, fill=color)

    def get_shadow(self) -> bool:
        return self._shadow_var.get()

    def get_split(self) -> bool:
        return self._split_var.get()

    def get_color(self):
        return self._color_picker.get()

    def get_opacity(self) -> float:
        return self._opacity_slider.get()

    def get_scale(self) -> float:
        return self._scale_slider.get()

    def get_feather(self) -> float:
        return self._feather_slider.get()


# ---------------------------------------------------------------------------
# PreviewPanel (centre)
# ---------------------------------------------------------------------------

class PreviewPanel(tk.Frame):
    """Central canvas for displaying the composited preview image."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=T.BG_DARKEST, **kwargs)
        self.app = app
        self._tk_image = None
        self._drag_start = None
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._build()

    def _build(self):
        # Toolbar strip
        bar = tk.Frame(self, bg=T.BG_DARK, height=36)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="Preview  —  drag overlay to reposition",
                 bg=T.BG_DARK, fg=T.TEXT_MUTED, font=T.FONT_SMALL).pack(side="left", padx=T.PAD)

        self._canvas = tk.Canvas(self, bg=T.BG_DARKEST,
                                 highlightthickness=0, cursor="fleur")
        self._canvas.pack(fill="both", expand=True)

        # Drag bindings
        self._canvas.bind("<ButtonPress-1>", self._drag_start_cb)
        self._canvas.bind("<B1-Motion>", self._drag_motion_cb)
        self._canvas.bind("<ButtonRelease-1>", self._drag_end_cb)

        # Placeholder text
        self._placeholder_id = self._canvas.create_text(
            400, 300, text="Upload a photo to begin\n✂ Hairify",
            fill=T.TEXT_MUTED, font=T.FONT_TITLE, justify="center"
        )

    def _drag_start_cb(self, event):
        self._drag_start = (event.x, event.y)

    def _drag_motion_cb(self, event):
        if self._drag_start is None:
            return
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self._drag_start = (event.x, event.y)
        self.app.nudge_overlay(dx, dy)

    def _drag_end_cb(self, event):
        self._drag_start = None

    def show_image(self, arr_rgba):
        """Display a (H, W, 4) RGBA NumPy array on the canvas."""
        from PIL import Image
        img = Image.fromarray(arr_rgba)
        # Fit to canvas size
        cw = self._canvas.winfo_width() or 700
        ch = self._canvas.winfo_height() or 600
        img.thumbnail((cw, ch), Image.LANCZOS)
        self._tk_image = ImageTk.PhotoImage(img)
        self._canvas.delete("all")
        self._canvas.create_image(cw // 2, ch // 2, image=self._tk_image, anchor="center")

    def clear(self):
        self._canvas.delete("all")
        self._placeholder_id = self._canvas.create_text(
            self._canvas.winfo_width() // 2 or 400,
            self._canvas.winfo_height() // 2 or 300,
            text="Upload a photo to begin\n✂ Hairify",
            fill=T.TEXT_MUTED, font=T.FONT_TITLE, justify="center"
        )


# ---------------------------------------------------------------------------
# GalleryPanel (right)
# ---------------------------------------------------------------------------

class GalleryPanel(tk.Frame):
    """Scrollable grid of hairstyle thumbnails."""

    THUMB = T.THUMB_SIZE

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=T.BG_DARK, width=T.RIGHT_PANEL_W, **kwargs)
        self.pack_propagate(False)
        self.app = app
        self._thumb_images = []   # keep references
        self._selected = None
        self._build()

    def _build(self):
        SectionHeader(self, "💈  Hairstyles").pack(anchor="w", padx=T.PAD,
                                                    pady=(T.PAD_LG, T.PAD))
        tk.Frame(self, bg=T.BORDER_COLOR, height=1).pack(fill="x")

        # Scrollable canvas
        container = tk.Frame(self, bg=T.BG_DARK)
        container.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(container, bg=T.BG_DARK,
                                 highlightthickness=0)
        scroll = tk.Scrollbar(container, orient="vertical",
                              command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=T.BG_DARK)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )
        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel scroll
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._inner.bind("<MouseWheel>", self._on_mousewheel)

    def populate(self, styles):
        """Populate the gallery with a list of HairstyleBase instances."""
        for widget in self._inner.winfo_children():
            widget.destroy()
        self._thumb_images.clear()

        cols = 2
        for idx, style in enumerate(styles):
            row, col = divmod(idx, cols)
            cell = tk.Frame(self._inner, bg=T.BG_CARD, padx=4, pady=4,
                            relief="flat")
            cell.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

            # Generate thumbnail
            thumb_arr = style.thumbnail(size=self.THUMB)
            from PIL import Image
            thumb_img = Image.fromarray(thumb_arr)
            tk_img = ImageTk.PhotoImage(thumb_img)
            self._thumb_images.append(tk_img)

            img_lbl = tk.Label(cell, image=tk_img, bg=T.BG_CARD,
                               cursor="hand2")
            img_lbl.pack()

            name_lbl = tk.Label(cell, text=style.name,
                                 bg=T.BG_CARD, fg=T.TEXT_PRIMARY,
                                 font=T.FONT_SMALL)
            name_lbl.pack()

            desc_lbl = tk.Label(cell, text=style.description,
                                  bg=T.BG_CARD, fg=T.TEXT_MUTED,
                                  font=("Segoe UI", 7), wraplength=self.THUMB)
            desc_lbl.pack()

            # Bind click
            for widget in (cell, img_lbl, name_lbl, desc_lbl):
                widget.bind("<Button-1>",
                            lambda e, s=style, c=cell: self._on_click(s, c))

        for c in range(cols):
            self._inner.columnconfigure(c, weight=1)

    def _on_click(self, style, cell):
        # Deselect previous
        if self._selected:
            try:
                self._selected.config(bg=T.BG_CARD)
                for child in self._selected.winfo_children():
                    child.config(bg=T.BG_CARD)
            except Exception:
                pass
        self._selected = cell
        cell.config(bg=T.BG_ELEVATED)
        for child in cell.winfo_children():
            child.config(bg=T.BG_ELEVATED)
        self.app.on_style_selected(style)

    def _on_inner_configure(self, _):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
