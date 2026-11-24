"""
style_catalog.py — Registry of all available hairstyles.

Usage:
    from hairstyles.style_catalog import CATALOG
    style = CATALOG["Bob Cut"]
    overlay = style.generate_overlay(400, 500)
"""

from hairstyles.styles.bob_cut import BobCut
from hairstyles.styles.pixie_cut import PixieCut
from hairstyles.styles.curly_afro import CurlyAfro
from hairstyles.styles.long_straight import LongStraight
from hairstyles.styles.long_wavy import LongWavy
from hairstyles.styles.man_bun import ManBun
from hairstyles.styles.undercut import Undercut
from hairstyles.styles.mohawk import Mohawk
from hairstyles.styles.cornrows import Cornrows
from hairstyles.styles.buzz_cut import BuzzCut

# Ordered list for gallery display
ALL_STYLES = [
    BobCut(),
    PixieCut(),
    CurlyAfro(),
    LongStraight(),
    LongWavy(),
    ManBun(),
    Undercut(),
    Mohawk(),
    Cornrows(),
    BuzzCut(),
]

# Dictionary for O(1) lookup by name
CATALOG = {style.name: style for style in ALL_STYLES}
