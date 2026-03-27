#!/usr/bin/env python3
"""
THE KING IN YELLOW — Pygame Graphical Edition (Visual Overhaul)
A Lovecraftian Dungeon Crawler with custom art assets.
"""

import os
import sys
import random

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    C, SCREEN_W, SCREEN_H, FPS, Assets, draw_hud,
    draw_text, draw_text_wrapped, fit_text, draw_text_fitted,
    draw_bar, draw_panel, draw_ornate_panel, draw_ornate_button,
    draw_gold_divider, hp_color, mad_color, rarity_color,
    generate_parchment_texture, draw_parchment_panel,
    draw_text_with_glow, draw_text_wrapped_glow, draw_text_fitted_glow,
    CLASS_COLORS, CLASS_ICONS,
)
from screens import (
    Screen, TitleScreen, ClassSelectScreen, ExploreScreen, CombatScreen,
    InventoryScreen, ShopScreen, RestScreen, LootScreen, EventScreen,
    TrapResultScreen, CombatResultScreen, LevelUpScreen, GameOverScreen,
    VictoryScreen, StatsScreen, SaveScreen, LoadScreen,
)

# ═══════════════════════════════════════════
# MAIN GAME CLASS
# ═══════════════════════════════════════════

class Game:
    def __init__(self):
        pygame.init()
        self.fullscreen = False
        try:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        except pygame.error as e:
            print(f"Display error: {e}")
            print("Try: export SDL_VIDEODRIVER=x11 (or wayland, windows, cocoa)")
            sys.exit(1)
        pygame.display.set_caption("The King in Yellow — A Lovecraftian Dungeon Crawler")
        self.clock = pygame.time.Clock()
        self.running = True

        self.assets = Assets()

        # Apply custom cursor if available
        if self.assets.cursor:
            try:
                pygame.mouse.set_cursor(self.assets.cursor)
            except Exception:
                pass  # Cursor format might not be supported on all platforms

        self.state = None

        # Shared state between screens
        self.gameover_msg = ""
        self.combat_result = {}
        self.pending_event = None
        self.shop_items = []
        self.shop_prices = []
        self.shop_sold = []
        self.shop_message = ""
        self.shop_msg_ok = True
        self.shop_msg_timer = 0
        self.trap_msg = ""
        self.trap_name = ""
        self.trap_desc = ""

        # Screens
        self.screens = {
            "title": TitleScreen(self),
            "class_select": ClassSelectScreen(self),
            "explore": ExploreScreen(self),
            "combat": CombatScreen(self),
            "inventory": InventoryScreen(self),
            "shop": ShopScreen(self),
            "rest": RestScreen(self),
            "loot": LootScreen(self),
            "event": EventScreen(self),
            "trap_result": TrapResultScreen(self),
            "combat_result": CombatResultScreen(self),
            "levelup": LevelUpScreen(self),
            "gameover": GameOverScreen(self),
            "victory": VictoryScreen(self),
            "save": SaveScreen(self),
            "load": LoadScreen(self),
            "stats": StatsScreen(self),
        }
        self.current_screen = self.screens["title"]
        self.current_screen.enter()

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    def get_bg(self, screen_name=None):
        """Get context-appropriate background, scaled to current window size."""
        if screen_name is None:
            screen_name = getattr(self, '_current_screen_name', "title")
        floor = self.state.floor if self.state else 1
        max_floor = self.state.max_floor if self.state else 20
        bg = self.assets.get_background(floor, max_floor, screen_name)
        if bg:
            sw, sh = self.screen.get_size()
            bw, bh = bg.get_size()
            if bw != sw or bh != sh:
                bg = pygame.transform.scale(bg, (sw, sh))
        return bg

    def switch_screen(self, name):
        if name in self.screens:
            self._current_screen_name = name
            self.current_screen = self.screens[name]
            self.current_screen.enter()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                else:
                    self.current_screen.handle_event(event)

            self.current_screen.update(dt)

            # Draw background
            bg = self.get_bg()
            if bg:
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill(C.DARK_BG)
            self.current_screen.draw(self.screen)

            pygame.display.flip()

        pygame.quit()


# ═══════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        import traceback
        print("\n" + "=" * 50)
        print("CRASH REPORT — The King in Yellow")
        print("=" * 50)
        traceback.print_exc()
        print("=" * 50)
        try:
            input("\nPress Enter to exit...")
        except EOFError:
            pass
    except KeyboardInterrupt:
        print("\n\nThe Yellow Sign fades. For now.")
        sys.exit(0)
