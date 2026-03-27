#!/usr/bin/env python3
"""
THE KING IN YELLOW — Pygame Graphical Edition (Visual Overhaul)
A Lovecraftian Dungeon Crawler with custom art assets.
"""

import os
import sys
import math
import random
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data import (
    CLASSES, BOSS, ENEMY_SPRITES, CLASS_ICONS, STAT_ICONS,
    EVENTS, TRAPS, RARITY_DATA, FLOOR_NARRATIVES, MAX_ACTIVE_SKILLS,
)
from engine import (
    GameState, generate_item, start_combat, player_use_skill,
    enemy_turn, process_status_effects, process_player_status_effects,
    tick_player_buffs, check_boss_phase, combat_run_attempt,
    generate_paths, advance_floor,
    resolve_event, resolve_trap, generate_shop, buy_shop_item,
)
from save_system import save_game, load_game, list_saves


# ═══════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════

SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

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
    OBSIDIAN         = (16, 12, 28)    # Deep dark base
    OBSIDIAN_DARK    = (10, 8, 20)     # Near-black for dark spots
    OBSIDIAN_MID     = (28, 20, 45)    # Mid-range surface color
    OBSIDIAN_EDGE    = (50, 35, 75)    # Edge/crack color (purple)
    OBSIDIAN_GLOW    = (80, 50, 130)   # Faint purple glow in edges
    # Eldritch text colors (on obsidian)
    ELDRITCH_GOLD    = (232, 185, 45)  # Primary text — eldritch gold
    ELDRITCH_GOLD_DIM = (180, 140, 35) # Dimmer gold for secondary text
    ELDRITCH_PURPLE  = (175, 130, 225) # Accent text — eldritch purple
    # Legacy aliases (point to obsidian/eldritch)
    PARCHMENT       = OBSIDIAN
    PARCHMENT_DARK  = OBSIDIAN_MID
    PARCHMENT_EDGE  = ELDRITCH_GOLD
    INK             = ELDRITCH_GOLD
    INK_LIGHT       = ELDRITCH_GOLD_DIM

# Class-specific colors
CLASS_COLORS = {
    "scholar": (180, 100, 230),    # bright violet — was ELDRITCH (too dark)
    "brute": (220, 50, 50),        # bright crimson — was CRIMSON (too dark)
    "warden": C.FROST,
    "shadowblade": C.MIST,
    "mad_prophet": C.MADNESS,
}

# Each class's thematic primary stat (used for icon display, not derived from max)
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


# ═══════════════════════════════════════════
# ASSET LOADER
# ═══════════════════════════════════════════

class Assets:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.cursor = None
        try:
            self.load()
        except Exception as e:
            print(f"FATAL: Asset loading failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def load(self):
        # --- Class sprites (for class select & combat) ---
        for class_id, filename in CLASS_SPRITE_FILES.items():
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.images[f"class_{class_id}"] = img
                    # Combat size
                    self.images[f"class_{class_id}_combat"] = pygame.transform.scale(img, (220, 220))
                    # Class select thumbnail
                    self.images[f"class_{class_id}_thumb"] = pygame.transform.scale(img, (90, 90))
                    print(f"  ✓ Class sprite loaded: {class_id} ({img.get_width()}x{img.get_height()})")
                except Exception as e:
                    print(f"  ✗ Warning: failed to load {path}: {e}")
            else:
                print(f"Warning: {path} not found")

        # --- Enemy sprites ---
        sprite_map = {
            "monster1": "transparent-lovecraftian-monster1.png",
            "monster3": "transparent-lovecraftian-monster3.png",
            "monster4": "transparent-lovecraftian-monster4.png",
            "monster5": "transparent-lovecraftian-monster5.png",
            "monster6": "transparent-lovecraftian-monster6.png",
            "monster7": "transparent-lovecraftian-monster7.png",
            "boss": "transparent-Boss.png",
        }
        for key, filename in sprite_map.items():
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.images[key] = img
                    self.images[f"{key}_combat"] = pygame.transform.scale(img, (240, 240))
                    self.images[f"{key}_small"] = pygame.transform.scale(img, (80, 80))
                except Exception as e:
                    print(f"Warning: failed to load {path}: {e}")
            else:
                print(f"Warning: {path} not found")

        # --- Backgrounds ---
        # Dungeon background (used for explore + combat floors 1-19)
        path = os.path.join(ASSETS_DIR, "Dungeon_background.jfif")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                self.images["bg_dungeon"] = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
            except Exception as e:
                print(f"Warning: failed to load dungeon bg: {e}")
        else:
            print(f"Warning: {path} not found")

        # Game over background
        path = os.path.join(ASSETS_DIR, "Game_Over_Screen.jfif")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                self.images["bg_gameover"] = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
            except Exception as e:
                print(f"Warning: failed to load gameover bg: {e}")
        else:
            print(f"Warning: {path} not found")

        # Boss background (the old bg_boss if it exists, or reuse dungeon)
        path = os.path.join(ASSETS_DIR, "bg_boss.jpg")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            self.images["bg_boss"] = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        else:
            self.images["bg_boss"] = self.images.get("bg_dungeon")

        # Title background (the old bg_title if it exists, or reuse dungeon)
        path = os.path.join(ASSETS_DIR, "bg_title.jpg")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            self.images["bg_title"] = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        else:
            self.images["bg_title"] = self.images.get("bg_dungeon")

        # --- Custom cursor ---
        path = os.path.join(ASSETS_DIR, "transparent-Cursor.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                cursor_scaled = pygame.transform.scale(img, (32, 32))
                cursors = pygame.cursors.Cursor((0, 0), cursor_scaled)
                self.cursor = cursors
            except Exception as e:
                print(f"Warning: failed to load cursor: {e}")

        # --- Text box sample (kept for reference/styling) ---
        path = os.path.join(ASSETS_DIR, "transparent-Text-box-Sample.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                self.images["text_box_sample"] = img
            except Exception as e:
                print(f"Warning: failed to load text box sample: {e}")

        # --- Stat icons (for stats screen + skill buttons) ---
        for stat_key, filename in STAT_ICONS.items():
            for size_suffix, size_px in [("32", 32), ("36", 36), ("48", 48), ("64", 64)]:
                path = os.path.join(ASSETS_DIR, f"{filename}_{size_suffix}.png")
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        self.images[f"stat_{stat_key}_{size_suffix}"] = img
                    except Exception as e:
                        print(f"Warning: failed to load {path}: {e}")

        # --- Path choice icons (for explore screen) ---
        for ptype, filename in PATH_ICON_FILES.items():
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.images[f"path_{ptype}"] = pygame.transform.scale(img, (150, 150))
                    print(f"  ✓ Path icon loaded: {ptype} ({filename})")
                except Exception as e:
                    print(f"Warning: failed to load path icon {path}: {e}")
            else:
                print(f"Warning: path icon not found: {path}")

        # --- Fonts ---
        self._load_fonts()

    def _load_fonts(self):
        # Title font: Cinzel Decorative (ornate Victorian/occult style)
        decor_path = os.path.join(FONTS_DIR, "CinzelDecorative-Regular.ttf")
        decor_bold_path = os.path.join(FONTS_DIR, "CinzelDecorative-Bold.ttf")
        cinzel_path = os.path.join(FONTS_DIR, "Cinzel.ttf")

        # Ensure we always have valid fonts
        fallback_sizes = {"title": 60, "title_sm": 40, "heading": 30,
                          "subheading": 28, "body": 24, "small": 20, "tiny": 17}

        def _test_font(font_obj):
            """Test if a font can actually render text. Returns True if valid."""
            try:
                surf = font_obj.render("Test", True, (255, 255, 255))
                return surf is not None
            except Exception:
                return False

        def _try_load_font(path, size, label):
            """Try loading a font from path. Returns valid font or None."""
            try:
                f = pygame.font.Font(path, size)
                if _test_font(f):
                    return f
                else:
                    print(f"  ✗ Font loaded but cannot render: {path} (size {size})")
                    return None
            except Exception as e:
                print(f"  ✗ Font load error: {path} — {e}")
                return None

        try:
            # Try CinzelDecorative for title/heading
            decor_loaded = False
            if os.path.exists(decor_path):
                f_title = _try_load_font(decor_path, 56, "title")
                f_title_sm = _try_load_font(decor_path, 36, "title_sm")
                f_heading = _try_load_font(decor_path, 28, "heading")
                if f_title and f_title_sm and f_heading:
                    self.fonts["title"] = f_title
                    self.fonts["title_sm"] = f_title_sm
                    self.fonts["heading"] = f_heading
                    decor_loaded = True
                    print(f"  ✓ Decorative font loaded: {decor_path}")

            if not decor_loaded:
                # Try bold variant
                if os.path.exists(decor_bold_path):
                    f_title = _try_load_font(decor_bold_path, 56, "title")
                    if f_title:
                        self.fonts["title"] = f_title
                        self.fonts["title_sm"] = _try_load_font(decor_bold_path, 36, "title_sm") or f_title
                        self.fonts["heading"] = _try_load_font(decor_bold_path, 28, "heading") or f_title
                        decor_loaded = True
                        print(f"  ✓ Decorative bold font loaded: {decor_bold_path}")

            if not decor_loaded:
                print(f"  ✗ No decorative font available, using system fallback")
                self.fonts["title"] = pygame.font.SysFont("serif", 62, bold=True)
                self.fonts["title_sm"] = pygame.font.SysFont("serif", 38, bold=True)
                self.fonts["heading"] = pygame.font.SysFont("serif", 32, bold=True)
        except Exception as e:
            print(f"  ✗ Decorative font section error: {e}")

        try:
            # Try Cinzel for body/UI
            cinzel_loaded = False
            if os.path.exists(cinzel_path):
                f_body = _try_load_font(cinzel_path, 22, "body")
                if f_body:
                    self.fonts["subheading"] = _try_load_font(cinzel_path, 26, "subheading") or f_body
                    self.fonts["body"] = f_body
                    self.fonts["small"] = _try_load_font(cinzel_path, 18, "small") or f_body
                    self.fonts["tiny"] = _try_load_font(cinzel_path, 15, "tiny") or f_body
                    cinzel_loaded = True
                    print(f"  ✓ Body font loaded: {cinzel_path}")

            if not cinzel_loaded:
                print(f"  ✗ No body font available, using system fallback")
                self.fonts["subheading"] = pygame.font.SysFont("georgia", 28, bold=True)
                self.fonts["body"] = pygame.font.SysFont("georgia", 22)
                self.fonts["small"] = pygame.font.SysFont("georgia", 18)
                self.fonts["tiny"] = pygame.font.SysFont("georgia", 15)
        except Exception as e:
            print(f"  ✗ Body font section error: {e}")

        # Final fallback — ensure ALL required fonts exist and can render
        for key, size in fallback_sizes.items():
            if key not in self.fonts or self.fonts[key] is None or not _test_font(self.fonts[key]):
                try:
                    fallback = pygame.font.Font(None, size)
                    if _test_font(fallback):
                        self.fonts[key] = fallback
                        print(f"  ✗ Font '{key}' using emergency default")
                    else:
                        # Absolute last resort
                        self.fonts[key] = pygame.font.SysFont("arial", size)
                        print(f"  ✗ Font '{key}' using arial fallback")
                except Exception:
                    self.fonts[key] = pygame.font.SysFont("arial", size)
                    print(f"  ✗ Font '{key}' using arial fallback (last resort)")

    def get_background(self, floor=1, max_floor=20, screen="explore"):
        """Get appropriate background for current context."""
        if screen == "title":
            bg = self.images.get("bg_title")
        elif screen == "gameover":
            bg = self.images.get("bg_gameover")
        elif screen == "boss" or floor >= max_floor:
            bg = self.images.get("bg_boss")
        else:
            bg = self.images.get("bg_dungeon")
        if not bg:
            return None
        # Darken overlay for readability
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        if screen == "gameover":
            overlay.fill((0, 0, 0, 100))
        else:
            overlay.fill((0, 0, 0, 140))
        result = bg.copy()
        result.blit(overlay, (0, 0))
        return result

    def get_sprite(self, enemy_name):
        """Get combat sprite by enemy name."""
        sprite_key = ENEMY_SPRITES.get(enemy_name)
        if sprite_key:
            return self.images.get(f"{sprite_key}_combat")
        return None

    def get_class_sprite(self, class_id, size="combat"):
        """Get class sprite for class select or combat."""
        key = f"class_{class_id}_{size}"
        return self.images.get(key)

    def get_class_combat(self, class_id):
        return self.images.get(f"class_{class_id}_combat")


# ═══════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════

def draw_text(surface, text, font, color, x, y, align="left"):
    """Draw text with alignment options."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if align == "center":
        rect.centerx = x
        rect.top = y
    elif align == "right":
        rect.right = x
        rect.top = y
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)
    return rect

def draw_text_wrapped(surface, text, font, color, x, y, max_width, line_height=None):
    """Draw text with word wrapping. Returns total height drawn."""
    if line_height is None:
        line_height = font.get_linesize()
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test = current_line + (" " if current_line else "") + word
        if font.size(test)[0] > max_width:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test
    if current_line:
        lines.append(current_line)

    for i, line_text in enumerate(lines):
        draw_text(surface, line_text, font, color, x, y + i * line_height)
    return len(lines) * line_height

def fit_text(font, text, max_pixel_width, suffix="…"):
    """Truncate text to fit within max_pixel_width pixels. Uses pixel-width measurement."""
    if font.size(text)[0] <= max_pixel_width:
        return text
    while len(text) > 0 and font.size(text + suffix)[0] > max_pixel_width:
        text = text[:-1]
    return text + suffix if text else suffix

def draw_text_fitted(surface, text, font, color, x, y, max_width, align="left"):
    """Draw text, auto-truncating to fit max_width pixels."""
    fitted = fit_text(font, text, max_width)
    draw_text(surface, fitted, font, color, x, y, align)

def draw_bar(surface, x, y, w, h, current, maximum, fg_color, bg_color=C.SHADOW, border_color=C.ASH):
    """Draw a horizontal bar (HP, XP, etc.)."""
    pygame.draw.rect(surface, border_color, (x - 1, y - 1, w + 2, h + 2), border_radius=3)
    pygame.draw.rect(surface, bg_color, (x, y, w, h), border_radius=2)
    if maximum > 0:
        fill_w = max(0, int(w * min(1, current / maximum)))
        if fill_w > 0:
            pygame.draw.rect(surface, fg_color, (x, y, fill_w, h), border_radius=2)

def draw_panel(surface, x, y, w, h, bg_color=None, border_color=C.GOLD_DIM, border_width=2):
    """Draw an obsidian panel with border."""
    texture = generate_parchment_texture(w, h)
    texture.set_alpha(235)
    surface.blit(texture, (x, y))
    pygame.draw.rect(surface, border_color, (x, y, w, h), border_width, border_radius=4)

def draw_ornate_panel(surface, x, y, w, h, title=None, title_color=None, title_font=None):
    """Draw an obsidian-textured panel with ornate gold frame."""
    draw_parchment_panel(surface, x, y, w, h, title=title, title_font=title_font)

def draw_ornate_button(surface, rect, text, font, hover=False, color=C.INK, disabled=False):
    """Draw a button styled with obsidian and gold trim borders."""
    # Obsidian fill for button
    btn_tex = generate_parchment_texture(rect.w, rect.h)
    btn_tex.set_alpha(240 if not hover else 255)
    surface.blit(btn_tex, (rect.x, rect.y))

    border_color = color if not disabled else C.ASH
    text_color = color if not disabled else C.ASH

    # Gold trim border
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=4)
    # Inner line
    inner_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.w - 6, rect.h - 6)
    dim_border = tuple(max(0, c - 60) for c in border_color)
    pygame.draw.rect(surface, dim_border, inner_rect, 1, border_radius=3)
    # Text with glow
    draw_text_with_glow(surface, text, font, text_color, rect.centerx,
                         rect.centery - font.get_height() // 2, align="center")
    # Hover glow effect
    if hover:
        glow = pygame.Surface((rect.w + 10, rect.h + 10), pygame.SRCALPHA)
        glow.fill((120, 80, 200, 40))
        surface.blit(glow, (rect.x - 5, rect.y - 5))

def draw_gold_divider(surface, x, y, width):
    """Draw a decorative gold divider line with end caps."""
    mid = width // 2
    pygame.draw.line(surface, C.GOLD_DIM, (x, y), (x + mid - 15, y), 1)
    pygame.draw.line(surface, C.GOLD_DIM, (x + mid + 15, y), (x + width, y), 1)
    # Center diamond
    pygame.draw.polygon(surface, C.GOLD_TRIM, [
        (x + mid, y - 4), (x + mid + 4, y),
        (x + mid, y + 4), (x + mid - 4, y)
    ])
    # End caps
    for ex in [x, x + width]:
        pygame.draw.circle(surface, C.GOLD_DIM, (ex, y), 2)

def hp_color(current, maximum):
    """Get HP bar color based on percentage."""
    if maximum <= 0:
        return C.HP_RED
    pct = current / maximum
    if pct > 0.6: return C.HP_GREEN
    elif pct > 0.3: return C.HP_YELLOW
    else: return C.HP_RED

def mad_color(madness):
    if madness < 30: return C.MIST
    elif madness < 60: return C.HP_YELLOW
    else: return C.HP_RED

def rarity_color(rarity):
    return {1: C.ASH, 2: C.MIST, 3: C.FROST, 4: C.CRIMSON}.get(rarity, C.ASH)


# ═══════════════════════════════════════════
# PARCHMENT TEXTURE & GLOW TEXT
# ═══════════════════════════════════════════

# ═══════════════════════════════════════════
# OBSIDIAN TEXTURE — TILE-BASED CACHING
# ═══════════════════════════════════════════
# Generate one 256x256 master tile with grain, patches, sparkles, cracks.
# Any panel tiles this master across its area, then adds edge effects + symbols.
# This replaces the old per-(w,h) cache that generated unique textures per size.

_OBSIDIAN_TILE_SIZE = 256
_obsidian_master_tile = None  # Lazily generated once


def _draw_yellow_sign(surf, cx, cy, size, alpha=18):
    """Draw a faded Yellow Sign (spiral + cross) — eldritch watermark."""
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    color = (200, 160, 40, alpha)
    points = []
    for a in range(0, 360 * 3, 5):
        rad = math.radians(a)
        r = (a / (360 * 3)) * size * 0.8
        px = size + int(r * math.cos(rad))
        py = size + int(r * math.sin(rad))
        points.append((px, py))
    if len(points) > 1:
        pygame.draw.lines(s, color, False, points, 1)
    bar = size // 3
    pygame.draw.line(s, color, (size - bar, size), (size + bar, size), 1)
    pygame.draw.line(s, color, (size, size - bar), (size, size + bar), 1)
    surf.blit(s, (cx - size, cy - size))

def _draw_elder_sign(surf, cx, cy, size, alpha=15):
    """Draw a faded Elder Sign (star in circle)."""
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    color = (140, 100, 200, alpha)
    pygame.draw.circle(s, color, (size, size), size - 2, 1)
    pts = []
    for i in range(10):
        rad = math.radians(i * 36 - 90)
        r = (size * 0.8) if i % 2 == 0 else (size * 0.35)
        pts.append((size + int(r * math.cos(rad)), size + int(r * math.sin(rad))))
    pygame.draw.polygon(s, color, pts, 1)
    surf.blit(s, (cx - size, cy - size))

def _draw_alchemical_circle(surf, cx, cy, size, alpha=12):
    """Draw a faded alchemical circle with triangle."""
    s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    color = (160, 120, 220, alpha)
    pygame.draw.circle(s, color, (size, size), size - 2, 1)
    pygame.draw.circle(s, color, (size, size), size - 6, 1)
    pts = []
    for i in range(3):
        rad = math.radians(i * 120 - 90)
        pts.append((size + int((size - 4) * math.cos(rad)), size + int((size - 4) * math.sin(rad))))
    pygame.draw.polygon(s, color, pts, 1)
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        dx = size + int((size - 2) * math.cos(rad))
        dy = size + int((size - 2) * math.sin(rad))
        pygame.draw.circle(s, color, (dx, dy), 2)
    surf.blit(s, (cx - size, cy - size))

def _draw_crack(surf, x, y, length, alpha=25):
    """Draw a random hairline crack."""
    color = (60, 40, 90, alpha)
    points = [(x, y)]
    cx, cy = x, y
    angle = random.uniform(0, 360)
    for _ in range(random.randint(3, 7)):
        angle += random.uniform(-40, 40)
        dist = random.randint(length // 3, length)
        rad = math.radians(angle)
        cx += int(dist * math.cos(rad))
        cy += int(dist * math.sin(rad))
        points.append((cx, cy))
    if len(points) > 1:
        pygame.draw.lines(surf, color, False, points, 1)


def _generate_obsidian_tile():
    """Generate the 256x256 master obsidian tile. Called once, cached forever."""
    global _obsidian_master_tile
    if _obsidian_master_tile is not None:
        return _obsidian_master_tile

    size = _OBSIDIAN_TILE_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    base = C.OBSIDIAN

    # Fill base — deep obsidian
    surf.fill((*base, 250))

    # Layer 1: Fine crystalline grain noise
    for _ in range(size * size // 3):
        px = random.randint(0, size - 1)
        py = random.randint(0, size - 1)
        v = random.randint(-12, 12)
        r = max(0, min(255, base[0] + v))
        g = max(0, min(255, base[1] + v))
        b = max(0, min(255, base[2] + v))
        surf.set_at((px, py), (r, g, b, 255))

    # Layer 2: Purple/indigo color variation patches
    for _ in range(max(4, size * size // 3000)):
        cx = random.randint(0, size)
        cy = random.randint(0, size)
        radius = random.randint(15, 40)
        spot = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for ring in range(radius, 0, -1):
            alpha = int(12 * (1 - ring / radius))
            purple_tint = (random.randint(20, 45), random.randint(10, 30), random.randint(40, 70))
            pygame.draw.circle(spot, (*purple_tint, alpha), (radius, radius), ring)
        surf.blit(spot, (cx - radius, cy - radius))

    # Layer 3: Bright crystalline sparkle points
    for _ in range(max(5, size * size // 2000)):
        sx = random.randint(0, size - 1)
        sy = random.randint(0, size - 1)
        sparkle = random.choice([
            (200, 160, 50, random.randint(15, 35)),   # Gold sparkle
            (140, 100, 190, random.randint(10, 25)),   # Purple sparkle
            (180, 170, 160, random.randint(8, 18)),    # Silver/white
        ])
        sz = random.randint(1, 3)
        pygame.draw.circle(surf, sparkle, (sx, sy), sz)

    # Layer 4: Cracks in the tile
    for _ in range(random.randint(2, 4)):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            _draw_crack(surf, random.randint(0, size), 0, random.randint(30, 80))
        elif edge == 'bottom':
            _draw_crack(surf, random.randint(0, size), size - 1, random.randint(30, 80))
        elif edge == 'left':
            _draw_crack(surf, 0, random.randint(0, size), random.randint(30, 80))
        else:
            _draw_crack(surf, size - 1, random.randint(0, size), random.randint(30, 80))

    # Layer 5: A few watermarks baked into the tile
    if size > 200:
        _draw_yellow_sign(surf, size // 3, size // 3, 20, alpha=14)
        _draw_elder_sign(surf, 2 * size // 3, 2 * size // 3, 15, alpha=10)

    _obsidian_master_tile = surf
    return surf


def generate_parchment_texture(width, height):
    """Generate a panel texture by tiling the master obsidian tile, then adding per-panel effects."""
    tile = _generate_obsidian_tile()
    tile_w, tile_h = tile.get_size()

    surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # Tile the master texture across the panel area
    for ty in range(0, height, tile_h):
        for tx in range(0, width, tile_w):
            surf.blit(tile, (tx, ty))

    # Per-panel: additional elritch symbols (unique per panel, not tiled)
    if width > 200 and height > 150:
        _draw_yellow_sign(surf, random.randint(width // 4, 3 * width // 4),
                         random.randint(height // 4, 3 * height // 4),
                         random.randint(25, 45), alpha=20)
        _draw_elder_sign(surf, random.randint(30, width - 30),
                        random.randint(30, height - 30),
                        random.randint(18, 30), alpha=16)
        if width > 400:
            _draw_alchemical_circle(surf, random.randint(50, width - 50),
                                   random.randint(50, height - 50),
                                   random.randint(20, 35), alpha=14)
        for _ in range(random.randint(2, 4)):
            sx = random.randint(15, width - 15)
            sy = random.randint(15, height - 15)
            if random.random() < 0.5:
                _draw_elder_sign(surf, sx, sy, random.randint(8, 14), alpha=10)
            else:
                _draw_alchemical_circle(surf, sx, sy, random.randint(10, 16), alpha=8)

    # Per-panel: edge glow — eldritch energy seeping through
    glow = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(25):
        alpha = int(35 * (1 - i / 25))
        edge_c = C.OBSIDIAN_GLOW
        pygame.draw.line(glow, (*edge_c, alpha), (0, i), (width, i))
        pygame.draw.line(glow, (*edge_c, alpha), (0, height - 1 - i), (width, height - 1 - i))
    for i in range(15):
        alpha = int(25 * (1 - i / 15))
        edge_c = C.OBSIDIAN_GLOW
        pygame.draw.line(glow, (*edge_c, alpha), (i, 0), (i, height))
        pygame.draw.line(glow, (*edge_c, alpha), (width - 1 - i, 0), (width - 1 - i, height))
    surf.blit(glow, (0, 0))

    # Per-panel: dark vignette
    vig = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(15):
        alpha = int(50 * (1 - i / 15))
        pygame.draw.line(vig, (0, 0, 0, alpha), (0, i), (width, i))
        pygame.draw.line(vig, (0, 0, 0, alpha), (0, height - 1 - i), (width, height - 1 - i))
    surf.blit(vig, (0, 0))

    return surf


def draw_parchment_panel(surface, x, y, w, h, title=None, title_font=None):
    """Draw an obsidian-textured panel with ornate gold frame borders."""
    # Generate and blit obsidian texture
    texture = generate_parchment_texture(w, h)
    surface.blit(texture, (x, y))

    # Outer frame — dark obsidian edge
    pygame.draw.rect(surface, C.OBSIDIAN_EDGE, (x, y, w, h), 3, border_radius=4)
    # Gold trim — outer
    pygame.draw.rect(surface, C.GOLD_TRIM, (x + 4, y + 4, w - 8, h - 8), 2, border_radius=3)
    # Gold trim — inner (dimmer)
    pygame.draw.rect(surface, C.GOLD_DIM, (x + 7, y + 7, w - 14, h - 14), 1, border_radius=2)

    # Corner ornaments (small gold diamonds)
    corners = [(x + 11, y + 11), (x + w - 11, y + 11),
               (x + 11, y + h - 11), (x + w - 11, y + h - 11)]
    for cx, cy in corners:
        pygame.draw.polygon(surface, C.GOLD_TRIM, [
            (cx, cy - 3), (cx + 3, cy), (cx, cy + 3), (cx - 3, cy)
        ])

    # Title bar
    if title and title_font:
        title_w = title_font.size(title)[0] + 30
        tx = x + w // 2 - title_w // 2
        # Small parchment strip behind title
        strip = generate_parchment_texture(title_w, 24)
        strip.set_alpha(200)
        surface.blit(strip, (tx, y - 2))
        pygame.draw.rect(surface, C.GOLD_DIM, (tx, y - 2, title_w, 24), 1, border_radius=2)
        draw_text_with_glow(surface, title, title_font, C.INK,
                            x + w // 2, y + 3, align="center")


# Glow text cache: key → (glow_surface, main_surface, text_w, text_h, glow_radius)
# Key = (text, font_id, color, glow_color, glow_radius)
# Limits to 4096 entries to avoid unbounded memory growth
_glow_text_cache = {}
_GLOW_CACHE_MAX = 4096


def _make_glow_cache_key(text, font, color, glow_color, glow_radius):
    """Build a hashable cache key for glow text."""
    return (text, id(font), color, glow_color, glow_radius)


def _render_glow_surface(text, font, glow_color, glow_radius):
    """Pre-compute a single surface with all glow layers composited."""
    # Render main text to get dimensions
    main_surf = font.render(text, True, (255, 255, 255))
    tw, th = main_surf.get_size()

    # Create a larger surface to contain the glow spread
    pad = glow_radius * 2 + 2
    gw, gh = tw + pad * 2, th + pad * 2
    glow_combined = pygame.Surface((gw, gh), pygame.SRCALPHA)

    # Draw each glow offset onto the combined surface
    for dx in range(-glow_radius, glow_radius + 1):
        for dy in range(-glow_radius, glow_radius + 1):
            if dx == 0 and dy == 0:
                continue
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > glow_radius:
                continue
            alpha = max(1, int(60 / (dist + 1)))
            glow_layer = font.render(text, True, glow_color)
            glow_layer.set_alpha(alpha)
            glow_combined.blit(glow_layer, (pad + dx, pad + dy))

    return glow_combined, pad


def draw_text_with_glow(surface, text, font, color, x, y, align="left",
                         glow_color=None, glow_radius=2):
    """Draw text with an ethereal purple glow/shadow for readability on obsidian.

    Uses a cache to pre-compute the glow surface once per unique (text, font, color, glow)
    combination, then blits the cached surface on subsequent calls. This reduces from
    ~25 font.render() calls per frame to 1 render + 2 blits on cache hit.
    """
    if glow_color is None:
        glow_color = (100, 60, 160)

    cache_key = _make_glow_cache_key(text, font, color, glow_color, glow_radius)

    cached = _glow_text_cache.get(cache_key)
    if cached is None:
        # Cache miss — compute glow surface + main text surface
        glow_surf, pad = _render_glow_surface(text, font, glow_color, glow_radius)
        main_surf = font.render(text, True, color)
        tw, th = main_surf.get_size()
        cached = (glow_surf, main_surf, tw, th, pad)
        # Evict oldest entries if cache is full (simple approach)
        if len(_glow_text_cache) >= _GLOW_CACHE_MAX:
            # Remove ~25% of oldest entries
            keys_to_remove = list(_glow_text_cache.keys())[:_GLOW_CACHE_MAX // 4]
            for k in keys_to_remove:
                del _glow_text_cache[k]
        _glow_text_cache[cache_key] = cached

    glow_surf, main_surf, tw, th, pad = cached

    # Calculate position based on alignment
    if align == "center":
        glow_x = x - tw // 2 - pad
        glow_y = y - pad
        main_x = x - tw // 2
        main_y = y
    elif align == "right":
        glow_x = x - tw - pad
        glow_y = y - pad
        main_x = x - tw
        main_y = y
    else:
        glow_x = x - pad
        glow_y = y - pad
        main_x = x
        main_y = y

    # Blit glow, then main text on top (2 blits total)
    surface.blit(glow_surf, (glow_x, glow_y))
    surface.blit(main_surf, (main_x, main_y))

    return pygame.Rect(main_x, main_y, tw, th)


def draw_text_wrapped_glow(surface, text, font, color, x, y, max_width,
                            line_height=None, glow_color=None):
    """Word-wrapped text with glow effect."""
    if line_height is None:
        line_height = font.get_linesize()
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test = current_line + (" " if current_line else "") + word
        if font.size(test)[0] > max_width:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test
    if current_line:
        lines.append(current_line)
    for i, line_text in enumerate(lines):
        draw_text_with_glow(surface, line_text, font, color, x, y + i * line_height,
                             glow_color=glow_color)
    return len(lines) * line_height


def draw_text_fitted_glow(surface, text, font, color, x, y, max_width,
                           align="left", glow_color=None):
    """Fitted (truncated) text with glow effect."""
    fitted = fit_text(font, text, max_width)
    draw_text_with_glow(surface, fitted, font, color, x, y, align, glow_color=glow_color)


# ═══════════════════════════════════════════
# SCREEN BASE CLASS
# ═══════════════════════════════════════════
