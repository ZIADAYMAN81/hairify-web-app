"""
theme.py — Dark glassmorphism design system for Hairify.

All color tokens, font definitions, and spacing constants live here.
"""

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

# Backgrounds
BG_DARKEST   = "#0d0d1a"   # root window background
BG_DARK      = "#13132b"   # panel background
BG_CARD      = "#1a1a36"   # card / widget surface
BG_GLASS     = "#1e1e40"   # glass panel background
BG_ELEVATED  = "#252550"   # elevated elements

# Accents
ACCENT_PRIMARY   = "#7c5cbf"   # purple
ACCENT_SECONDARY = "#3ecfcf"   # teal
ACCENT_HOVER     = "#9b7fd4"   # lighter purple on hover
ACCENT_ACTIVE    = "#5e3d99"   # darker purple when pressed

# Text
TEXT_PRIMARY   = "#f0eeff"
TEXT_SECONDARY = "#a89ec9"
TEXT_MUTED     = "#6a628a"
TEXT_ACCENT    = "#3ecfcf"

# Status
SUCCESS = "#3ecf8e"
WARNING = "#f0c060"
ERROR   = "#ef5f5f"

# Divider / border
BORDER_COLOR  = "#2e2e5c"
BORDER_LIGHT  = "#3d3d70"

# Split-view divider
SPLIT_LINE = "#ffffff"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
# Tkinter font tuples: (family, size, weight)

FONT_TITLE   = ("Segoe UI", 20, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 11)
FONT_SMALL   = ("Segoe UI",  9)
FONT_MONO    = ("Consolas",  10)
FONT_BTN     = ("Segoe UI", 11, "bold")
FONT_LABEL   = ("Segoe UI", 10)

# ---------------------------------------------------------------------------
# Spacing / geometry
# ---------------------------------------------------------------------------

PAD = 12          # standard padding
PAD_SM = 6        # small padding
PAD_LG = 20       # large padding

RADIUS = 10       # button corner radius
CARD_RADIUS = 14  # card corner radius

LEFT_PANEL_W  = 240
RIGHT_PANEL_W = 260
MIN_W = 1100
MIN_H = 720

THUMB_SIZE = 110  # gallery thumbnail px

# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------
HOVER_STEP_MS = 16    # ~60 fps animation tick
FADE_STEPS    = 8
