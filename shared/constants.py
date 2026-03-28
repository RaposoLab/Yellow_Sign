"""
THE KING IN YELLOW — Shared Constants
Screen dimensions, color palette, class mappings, path icons.
"""

import os

# ═══════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

# Lovecraftian color palette
class C:
    VOID       = (26, 10, 46)
    SHADOW     = (45, 27, 78)
    ELDRITCH   = (74, 14, 78)
    YELLOW     = (212, 160, 23)
    AMBER      = (184, 134, 11)
    BONE       = (212, 197, 169)
    CRIMSON    = (139, 0, 0)
    BLOOD      = (196, 30, 58)
    MIST       = (143, 188, 143)
    FROST      = (70, 130, 180)
    EMBER      = (255, 69, 0)
    MADNESS    = (255, 99, 71)
    GOLD       = (241, 196, 15)
    ASH        = (105, 105, 105)
    LIGHTNING  = (0, 191, 255)
    BLACK      = (0, 0, 0)
    WHITE      = (255, 255, 255)
    DARK_BG    = (12, 6, 24)
    PANEL_BG   = (20, 12, 38)
    HP_GREEN   = (46, 204, 113)
    HP_YELLOW  = (243, 156, 18)
    HP_RED     = (231, 76, 60)
    XP_PURPLE  = (155, 89, 182)
    SHIELD_BLUE = (52, 152, 219)
    GOLD_TRIM  = (218, 165, 32)
    GOLD_DIM   = (139, 101, 20)
    # Obsidian / dark stone aesthetic
    OBSIDIAN         = (16, 12, 28)
    OBSIDIAN_DARK    = (10, 8, 20)
    OBSIDIAN_MID     = (28, 20, 45)
    OBSIDIAN_EDGE    = (50, 35, 75)
    OBSIDIAN_GLOW    = (80, 50, 130)
    # Eldritch text colors (on obsidian)
    ELDRITCH_GOLD    = (232, 185, 45)
    ELDRITCH_GOLD_DIM = (180, 140, 35)
    ELDRITCH_PURPLE  = (175, 130, 225)
    # Legacy aliases
    PARCHMENT       = OBSIDIAN
    PARCHMENT_DARK  = OBSIDIAN_MID
    PARCHMENT_EDGE  = ELDRITCH_GOLD
    INK             = ELDRITCH_GOLD
    INK_LIGHT       = ELDRITCH_GOLD_DIM

# Class-specific colors
CLASS_COLORS = {
    "scholar": (180, 100, 230),
    "brute": (220, 50, 50),
    "warden": C.FROST,
    "shadowblade": C.MIST,
    "mad_prophet": C.MADNESS,
}

# Each class's thematic primary stat
CLASS_PRIMARY_STAT = {
    "scholar": "int",
    "brute": "str",
    "warden": "wis",
    "shadowblade": "agi",
    "mad_prophet": "luck",
}

# Map class_id → sprite filename
CLASS_SPRITE_FILES = {
    "scholar": "transparent-Int-basedClass.png",
    "brute": "transparent-Strenght-basedClass.png",
    "warden": "wis-character.png",
    "shadowblade": "transparent-Agi-basedClass.png",
    "mad_prophet": "transparent-luck-basedClass.png",
}

# Path type → icon filename for exploration path choices
PATH_ICON_FILES = {
    "combat": "Enemy_Ahead_F.png",
    "shop": "Shop_Ahead_F.png",
    "rest": "Rest_Ahead_F.jfif",
    "loot": "Item_Ahead.png",
    "event": "Decision_Ahead.png",
    "trap": "Decision_Ahead.png",
    "boss": "Boss_Ahead_F.png",
}
