#!/usr/bin/env python3
"""
THE KING IN YELLOW — Pygame Graphical Edition (Visual Overhaul)
A Lovecraftian Dungeon Crawler with custom art assets.
"""

import os
import sys
import random

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared import (
    C,
    SCREEN_W,
    SCREEN_H,
    FPS,
    Assets,
    draw_hud,
    draw_text,
    draw_text_wrapped,
    fit_text,
    draw_text_fitted,
    draw_bar,
    draw_panel,
    draw_ornate_panel,
    draw_ornate_button,
    draw_gold_divider,
    hp_color,
    mad_color,
    rarity_color,
    generate_parchment_texture,
    draw_parchment_panel,
    draw_text_with_glow,
    draw_text_wrapped_glow,
    draw_text_fitted_glow,
    CLASS_COLORS,
    CLASS_ICONS,
    LightingSystem,
)
from screens import (
    Screen,
    TitleScreen,
    ClassSelectScreen,
    ExploreScreen,
    CombatScreen,
    InventoryScreen,
    ShopScreen,
    RestScreen,
    LootScreen,
    EventScreen,
    TrapResultScreen,
    CombatResultScreen,
    LevelUpScreen,
    GameOverScreen,
    VictoryScreen,
    StatsScreen,
    SaveScreen,
    LoadScreen,
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

        # Track total game time for animations
        self.time_seconds = 0.0

        # Apply custom cursor if available
        if self.assets.cursor:
            try:
                pygame.mouse.set_cursor(self.assets.cursor)
            except Exception:
                pass  # Cursor format might not be supported on all platforms

        self.state = None

        # Dynamic lighting system
        self.lighting = LightingSystem()

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

        # Screen transition state (fade-to-black)
        self.transition = None  # None, "fadeOut", "fadeIn"
        self.transition_timer = 0
        self.transition_duration = 0.3  # seconds per phase
        self._pending_screen = None
        self._transition_surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

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
            screen_name = getattr(self, "_current_screen_name", "title")
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
        if name not in self.screens:
            return
        if self.transition is not None:
            # Already transitioning — force complete immediately
            self._finish_transition(name)
            return
        self.transition = "fadeOut"
        self.transition_timer = 0
        self._pending_screen = name

    def _finish_transition(self, name=None):
        """Immediately complete a pending or forced transition."""
        target = name or self._pending_screen
        if target and target in self.screens:
            self._prev_screen_name = getattr(self, "_current_screen_name", "title")
            self._current_screen_name = target
            self.current_screen = self.screens[target]
            self.current_screen.enter()
        self.transition = None
        self.transition_timer = 0
        self._pending_screen = None

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # Handle transition timing
            if self.transition:
                self.transition_timer += dt
                if self.transition == "fadeOut" and self.transition_timer >= self.transition_duration:
                    # Fade-out complete — switch screen and start fade-in
                    self._finish_transition()
                    self.transition = "fadeIn"
                    self.transition_timer = 0
                elif self.transition == "fadeIn" and self.transition_timer >= self.transition_duration:
                    # Fade-in complete
                    self.transition = None
                    self.transition_timer = 0

            # During fade-out block input to the old screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif not self.transition:
                    self.current_screen.handle_event(event)

            if not self.transition or self.transition == "fadeIn":
                self.current_screen.update(dt)

            # Update total game time for animations
            self.time_seconds += dt

            # Draw background
            bg = self.get_bg()
            if bg:
                self.screen.blit(bg, (0, 0))
            else:
                self.screen.fill(C.DARK_BG)
            self.current_screen.draw(self.screen)

            # Update and draw dynamic lighting overlay
            if self.state and getattr(self, "_current_screen_name", None) not in ("title", "class_select"):
                hp_ratio = self.state.hp / max(1, self.state.max_hp)
                s = self.state
                self.lighting.update_state(
                    hp_ratio=hp_ratio,
                    madness=s.madness,
                    floor=s.floor,
                    max_floor=s.max_floor,
                    in_combat=(getattr(self, "_current_screen_name", None) == "combat"),
                    enemy_hp_ratio=(
                        (s.enemy_hp / max(1, s.enemy_max_hp))
                        if hasattr(s, "enemy_hp") and s.enemy_max_hp > 0
                        else 1.0
                    ),
                    is_boss=getattr(s, "enemy_is_boss", False),
                )
                self.lighting.draw(self.screen, self.time_seconds)

            # Draw transition overlay
            if self.transition:
                progress = min(1.0, self.transition_timer / self.transition_duration)
                if self.transition == "fadeOut":
                    alpha = int(255 * progress)
                else:  # fadeIn
                    alpha = int(255 * (1.0 - progress))
                self._transition_surface.fill((0, 0, 0, alpha))
                self.screen.blit(self._transition_surface, (0, 0))

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
