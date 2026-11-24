"""
widgets.py — Custom Tkinter widgets for Hairify.

Includes:
  - RoundedButton   : animated hover button drawn on Canvas
  - ColorPicker     : inline R/G/B sliders + hex preview
  - StatusBar       : bottom status line with icon
  - LabeledSlider   : styled Tkinter Scale with label
  - SectionHeader   : styled section header
"""

import tkinter as tk
from typing import Callable, Optional, Tuple
from gui import theme as T


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hex_lerp(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colours."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + t * (r2 - r1))
    g = int(g1 + t * (g2 - g1))
    b = int(b1 + t * (b2 - b1))
    return f"#{r:02x}{g:02x}{b:02x}"


# ---------------------------------------------------------------------------
# RoundedButton
# ---------------------------------------------------------------------------

class RoundedButton(tk.Canvas):
    """A button drawn on a Canvas with rounded corners and hover animation."""

    def __init__(self, parent, text: str, command: Callable = None,
                 width: int = 160, height: int = 38,
                 bg: str = T.ACCENT_PRIMARY,
                 bg_hover: str = T.ACCENT_HOVER,
                 fg: str = T.TEXT_PRIMARY,
                 font=T.FONT_BTN,
                 radius: int = T.RADIUS,
                 icon: str = ""):
        # Pass only plain canvas options — no custom kwargs forwarded
        super().__init__(parent, width=width, height=height,
                         background=T.BG_DARK, highlightthickness=0)
        self._text = text
        self._icon = icon
        self._command = command
        self._fill = bg
        self._fill_hover = bg_hover
        self._text_color = fg
        self._font = font
        self._radius = radius
        self._btn_w = width
        self._btn_h = height
        self._hover_t = 0.0

        self._drawn = False
        self.bind("<Map>", self._on_map)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_map(self, _=None):
        if not self._drawn:
            self._drawn = True
            self._draw(self._fill)

    def _draw(self, color: str):
        self.delete("all")
        r = self._radius
        w, h = self._btn_w, self._btn_h
        self.create_polygon(
            r, 0,  w - r, 0,
            w, r,  w, h - r,
            w - r, h,  r, h,
            0, h - r,  0, r,
            smooth=True, fill=color, outline=""
        )
        label = f"{self._icon}  {self._text}" if self._icon else self._text
        self.create_text(w // 2, h // 2, text=label,
                         fill=self._text_color, font=self._font)

    def _on_enter(self, _):
        self._animate_hover(forward=True)

    def _on_leave(self, _):
        self._animate_hover(forward=False)

    def _animate_hover(self, forward: bool):
        step = 1.0 / T.FADE_STEPS
        if forward:
            self._hover_t = min(1.0, self._hover_t + step)
        else:
            self._hover_t = max(0.0, self._hover_t - step)
        color = _hex_lerp(self._fill, self._fill_hover, self._hover_t)
        self._draw(color)
        done = (forward and self._hover_t >= 1.0) or \
               (not forward and self._hover_t <= 0.0)
        if not done:
            self.after(T.HOVER_STEP_MS,
                       lambda: self._animate_hover(forward))

    def _on_press(self, _):
        self._draw(T.ACCENT_ACTIVE)

    def _on_release(self, _):
        self._draw(_hex_lerp(self._fill, self._fill_hover, self._hover_t))
        if self._command:
            self._command()

    def configure_text(self, text: str):
        self._text = text
        self._draw(_hex_lerp(self._fill, self._fill_hover, self._hover_t))


# ---------------------------------------------------------------------------
# ColorPicker
# ---------------------------------------------------------------------------

class ColorPicker(tk.Frame):
    """Inline R/G/B slider color picker."""

    def __init__(self, parent, label: str = "Hair Color",
                 initial: Tuple[int, int, int] = (50, 25, 10),
                 on_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, bg=T.BG_CARD, **kwargs)
        self._on_change = on_change
        self._r = tk.IntVar(value=initial[0])
        self._g = tk.IntVar(value=initial[1])
        self._b = tk.IntVar(value=initial[2])

        tk.Label(self, text=label, bg=T.BG_CARD,
                 fg=T.TEXT_SECONDARY, font=T.FONT_LABEL).pack(anchor="w", padx=T.PAD_SM)

        self._preview = tk.Label(self, width=4, height=1,
                                 bg=self._hex(), relief="flat")
        self._preview.pack(side="right", padx=T.PAD_SM, pady=4)

        for name, var, color in [("R", self._r, "#ef5f5f"),
                                  ("G", self._g, "#3ecf8e"),
                                  ("B", self._b, "#5f9fef")]:
            row = tk.Frame(self, bg=T.BG_CARD)
            row.pack(fill="x", padx=T.PAD_SM, pady=2)
            tk.Label(row, text=name, bg=T.BG_CARD, fg=color,
                     font=T.FONT_SMALL, width=2).pack(side="left")
            s = tk.Scale(row, from_=0, to=255, orient="horizontal",
                         variable=var, bg=T.BG_CARD, fg=color,
                         troughcolor=T.BG_ELEVATED, highlightthickness=0,
                         command=self._slider_changed, showvalue=False)
            s.pack(side="left", fill="x", expand=True)

    def _slider_changed(self, _=None):
        self._preview.config(bg=self._hex())
        if self._on_change:
            self._on_change(self.get())

    def _hex(self) -> str:
        return f"#{self._r.get():02x}{self._g.get():02x}{self._b.get():02x}"

    def get(self) -> Tuple[int, int, int]:
        return (self._r.get(), self._g.get(), self._b.get())

    def set(self, rgb: Tuple[int, int, int]):
        self._r.set(rgb[0])
        self._g.set(rgb[1])
        self._b.set(rgb[2])
        self._preview.config(bg=self._hex())


# ---------------------------------------------------------------------------
# LabeledSlider
# ---------------------------------------------------------------------------

class LabeledSlider(tk.Frame):
    """A horizontal slider with label and live value display."""

    def __init__(self, parent, label: str, from_: float, to: float,
                 initial: float, on_change: Optional[Callable] = None,
                 resolution: float = 0.01, **kwargs):
        super().__init__(parent, bg=T.BG_CARD, **kwargs)
        self._on_change = on_change
        self._var = tk.DoubleVar(value=initial)

        row = tk.Frame(self, bg=T.BG_CARD)
        row.pack(fill="x", padx=T.PAD_SM)
        tk.Label(row, text=label, bg=T.BG_CARD,
                 fg=T.TEXT_SECONDARY, font=T.FONT_LABEL).pack(side="left")
        self._val_lbl = tk.Label(row, text=f"{initial:.2f}",
                                 bg=T.BG_CARD, fg=T.TEXT_ACCENT,
                                 font=T.FONT_SMALL)
        self._val_lbl.pack(side="right")

        self._scale = tk.Scale(
            self, from_=from_, to=to, orient="horizontal",
            variable=self._var, bg=T.BG_CARD, fg=T.TEXT_PRIMARY,
            troughcolor=T.BG_ELEVATED, highlightthickness=0,
            showvalue=False, resolution=resolution,
            command=self._changed,
        )
        self._scale.pack(fill="x", padx=T.PAD_SM, pady=(0, 4))

    def _changed(self, _=None):
        v = self._var.get()
        self._val_lbl.config(text=f"{v:.2f}")
        if self._on_change:
            self._on_change(v)

    def get(self) -> float:
        return self._var.get()

    def set(self, value: float):
        self._var.set(value)
        self._val_lbl.config(text=f"{value:.2f}")


# ---------------------------------------------------------------------------
# StatusBar
# ---------------------------------------------------------------------------

class StatusBar(tk.Frame):
    """Bottom bar showing detection status and hints."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=T.BG_DARKEST, height=28, **kwargs)
        self.pack_propagate(False)
        self._label = tk.Label(self, text="Ready — Upload a photo to begin",
                               bg=T.BG_DARKEST, fg=T.TEXT_MUTED,
                               font=T.FONT_SMALL, anchor="w")
        self._label.pack(side="left", padx=T.PAD)

    def set(self, msg: str, color: str = T.TEXT_MUTED):
        self._label.config(text=msg, fg=color)


# ---------------------------------------------------------------------------
# SectionHeader
# ---------------------------------------------------------------------------

class SectionHeader(tk.Label):
    """A styled section header label."""

    def __init__(self, parent, text: str, **kwargs):
        super().__init__(parent, text=text,
                         bg=T.BG_DARK, fg=T.ACCENT_SECONDARY,
                         font=T.FONT_HEADING, anchor="w",
                         **kwargs)
