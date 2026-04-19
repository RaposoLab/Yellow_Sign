"""
THE KING IN YELLOW — Dynamic Lighting System

Provides atmospheric lighting effects for the horror aesthetic:
  - HP-based vignette: screen edges darken and redden as HP drops
  - Torch flicker: ambient light sources with realistic fire-like flicker
  - Status glow: colored aura based on active status effects (poison=green, burn=orange, etc.)
  - Depth darkness: progressive darkening as the player descends deeper
  - Ambient breathing: subtle light/dark cycle for unease

Architecture:
  - LightingSystem class holds state and cached surfaces
  - Called from pygame_game.py after screen.draw() but before transition overlay
  - Screens can register light sources via add_light() / remove_light()
  - Uses SRCALPHA surfaces composited with BLEND_RGBA_ADD for glow
  - Full-screen darkness overlay with radial-gradient "light holes" punched in
"""

import math
import random

import pygame

from shared.constants import SCREEN_W, SCREEN_H

# ═══════════════════════════════════════════
# LIGHT SOURCE DEFINITIONS
# ═══════════════════════════════════════════

# Colors for different status glow effects
_STATUS_GLOW_COLORS = {
    "burning": (255, 120, 30),     # Fierce orange
    "poisoned": (80, 220, 60),     # Sickly green
    "bleeding": (180, 30, 30),     # Deep crimson
    "weakened": (150, 150, 80),    # Faded yellow
    "freezing": (100, 180, 255),   # Icy blue
    "petrified": (140, 120, 100),  # Stone gray-brown
    "doom": (100, 0, 50),          # Dark magenta
}

# Torch light color: warm amber with slight gold tint
_TORCH_COLOR = (255, 190, 100)
_TORCH_FLICKER_COLOR = (255, 160, 60)

# HP-based vignette colors (interpolated based on HP percentage)
_HP_VIGNETTE_HIGH = (0, 0, 0, 0)       # No vignette at full HP
_HP_VIGNETTE_LOW = (40, 0, 0, 180)     # Deep red vignette at critical HP

# Depth darkness: maximum alpha per depth zone
_DEPTH_DARKNESS = {
    # floor_range: (ambient_alpha, torch_radius_mult, vignette_intensity)
    (1, 4):   (0,    1.0, 0.0),    # The Asylum: safe, well-lit
    (5, 8):   (20,   0.95, 0.1),   # The Depths Below: slight darkness
    (9, 12):  (40,   0.85, 0.25),  # The Descent: growing unease
    (13, 16): (60,   0.75, 0.4),   # Approaching the Threshold: oppressive
    (17, 20): (80,   0.6,  0.55),  # The Spiral: near-pitch black
}

# Cache settings
_LIGHT_TEXTURE_CACHE_SIZE = 6
_LIGHT_TEXTURE_MAX_RADIUS = 512


# ═══════════════════════════════════════════
# RADIAL GRADIENT LIGHT TEXTURE GENERATOR
# ═══════════════════════════════════════════

_light_texture_cache: dict = {}


def _get_light_texture(radius: int, color: tuple, intensity: float = 1.0) -> pygame.Surface:
    """Get or generate a cached radial gradient light texture.

    Creates a pre-rendered circular gradient that goes from the given color
    at the center to fully transparent at the edges. Used as a "stamp" for
    light sources, blitted with BLEND_RGBA_ADD for additive glow.

    Args:
        radius: Radius of the light in pixels
        color: RGB color tuple for the light
        intensity: Brightness multiplier (0.0 to 1.0)

    Returns:
        A pygame Surface with the radial gradient, sized (radius*2, radius*2)
    """
    # Clamp radius to prevent excessive memory use
    radius = min(radius, _LIGHT_TEXTURE_MAX_RADIUS)
    # Quantize for caching (step of 4px for radius, 10 for intensity)
    cache_key = (radius // 4, color, int(intensity * 10))
    if cache_key in _light_texture_cache:
        return _light_texture_cache[cache_key]

    size = radius * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # Draw concentric circles from outside in — inner circles overwrite outer
    num_rings = min(radius, 60)  # Cap rings for performance
    for i in range(num_rings, 0, -1):
        ratio = i / num_rings
        # Alpha falls off with a quadratic curve for realistic falloff
        alpha = int(255 * intensity * (1 - ratio * ratio) * 0.35)
        if alpha < 1:
            continue
        ring_radius = int(radius * ratio)
        r = min(255, int(color[0] * (1 - ratio * 0.2)))
        g = min(255, int(color[1] * (1 - ratio * 0.3)))
        b = min(255, int(color[2] * (1 - ratio * 0.4)))
        pygame.draw.circle(surf, (r, g, b, alpha), (radius, radius), ring_radius)

    # Manage cache size
    if len(_light_texture_cache) >= _LIGHT_TEXTURE_CACHE_SIZE:
        # Remove oldest entry
        oldest_key = next(iter(_light_texture_cache))
        del _light_texture_cache[oldest_key]
    _light_texture_cache[cache_key] = surf
    return surf


# ═══════════════════════════════════════════
# TORCH FLICKER ENGINE
# ═══════════════════════════════════════════

class TorchFlicker:
    """Simulates realistic torch-like light flicker using multiple sine waves.

    Combines several oscillators at different frequencies and amplitudes
    to create an organic, non-repeating flicker pattern. The result is
    a smooth variation in light intensity and slight color temperature
    shifts between warm amber and hot orange.
    """

    def __init__(self):
        # Multiple frequency components for organic flicker
        self._phases = [random.uniform(0, math.tau) for _ in range(5)]
        self._freqs = [1.7, 3.1, 5.3, 0.7, 8.9]   # Hz
        self._amps = [0.15, 0.10, 0.08, 0.20, 0.04]  # Intensity contribution

    def get_intensity(self, time_seconds: float) -> float:
        """Get current flicker intensity (0.0 to 1.0+).

        Combines multiple sine waves with different frequencies and
        random phase offsets. The result is a smooth but non-repeating
        flicker pattern that mimics real firelight.

        Args:
            time_seconds: Total elapsed game time

        Returns:
            Intensity multiplier (typically 0.5 to 1.1)
        """
        val = 0.7  # Base intensity (torches never fully extinguish)
        for i, (phase, freq, amp) in enumerate(zip(self._phases, self._freqs, self._amps)):
            # Slow phase drift for non-repeating pattern
            drift = time_seconds * 0.13 * (i + 1)
            val += amp * math.sin(time_seconds * freq + phase + drift)
        return max(0.3, min(1.15, val))

    def get_color(self, time_seconds: float) -> tuple:
        """Get current torch color with slight temperature shift.

        The torch shifts between warm amber and hotter orange-yellow
        as different "flame" components dominate, simulating the
        color variation of real firelight.

        Args:
            time_seconds: Total elapsed game time

        Returns:
            RGB tuple (typically orange to gold range)
        """
        temp_shift = 0.5 + 0.5 * math.sin(time_seconds * 1.7)
        r = int(_TORCH_COLOR[0] * (0.9 + 0.1 * temp_shift))
        g = int(_TORCH_FLICKER_COLOR[1] * (0.8 + 0.2 * (1 - temp_shift)))
        b = int(_TORCH_COLOR[2] * (0.5 + 0.5 * temp_shift))
        return (min(255, r), min(255, g), min(255, b))


# ═══════════════════════════════════════════
# LIGHT SOURCE
# ═══════════════════════════════════════════

class LightSource:
    """A single point light source in the scene.

    Each light source has a position, color, radius, and intensity.
    Lights can optionally flicker (like torches) or be static (like
    status effect glows).

    Args:
        x: X position on screen
        y: Y position on screen
        radius: Light radius in pixels
        color: RGB color tuple
        intensity: Base brightness (0.0 to 1.0)
        flicker: If True, apply torch-like flicker animation
        pulse_speed: Speed of gentle pulsing (0 = no pulse)
    """

    def __init__(self, x: int, y: int, radius: int = 200, color: tuple = _TORCH_COLOR,
                 intensity: float = 0.7, flicker: bool = False, pulse_speed: float = 0.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.base_intensity = intensity
        self.flicker = flicker
        self.pulse_speed = pulse_speed
        self._flicker = TorchFlicker() if flicker else None

    def get_current_intensity(self, time_seconds: float) -> float:
        """Get current intensity including flicker and pulse."""
        intensity = self.base_intensity
        if self._flicker:
            intensity *= self._flicker.get_intensity(time_seconds)
        if self.pulse_speed > 0:
            pulse = 0.5 + 0.5 * math.sin(time_seconds * self.pulse_speed)
            intensity *= (0.85 + 0.15 * pulse)
        return max(0.0, min(1.0, intensity))

    def get_current_color(self, time_seconds: float) -> tuple:
        """Get current color including flicker temperature shift."""
        if self._flicker:
            return self._flicker.get_color(time_seconds)
        return self.color


# ═══════════════════════════════════════════
# MAIN LIGHTING SYSTEM
# ═══════════════════════════════════════════

class LightingSystem:
    """Central lighting system for the entire game.

    Manages all dynamic light sources and renders a combined lighting
    overlay each frame. The overlay is composited on top of the game
    scene to create atmospheric lighting effects.

    The system renders in layers:
    1. Depth-based ambient darkness overlay
    2. HP-based vignette (red tint at low HP)
    3. Light sources (torch flicker, status glows)
    4. Subtle ambient breathing effect

    Usage:
        lighting = LightingSystem()
        lighting.add_torch(640, 360, radius=250)
        lighting.set_status_effects(["burning", "poisoned"])
        # In game loop:
        lighting.update(dt, time_seconds, game_state)
        lighting.draw(surface)
    """

    def __init__(self):
        self.lights: list = []
        self._status_effects: list = []
        self._hp_ratio: float = 1.0
        self._madness: float = 0.0
        self._floor: int = 1
        self._max_floor: int = 20
        self._in_combat: bool = False
        self._enemy_hp_ratio: float = 1.0
        self._boss: bool = False
        self._enabled: bool = True

        # Cached overlay surface (reused each frame)
        self._overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        # Ambient torches for non-combat screens
        self._ambient_torches: list = []
        self._setup_ambient_torches()

    def _setup_ambient_torches(self):
        """Create ambient torch positions for atmospheric lighting."""
        # Two torches flanking the screen edges, like wall sconces
        self._ambient_torches = [
            LightSource(80, SCREEN_H // 2 - 40, radius=280, color=_TORCH_COLOR,
                        intensity=0.35, flicker=True),
            LightSource(SCREEN_W - 80, SCREEN_H // 2 - 40, radius=280, color=_TORCH_COLOR,
                        intensity=0.35, flicker=True),
            # Central ceiling light (dimmer)
            LightSource(SCREEN_W // 2, 60, radius=350, color=(200, 180, 140),
                        intensity=0.2, flicker=True),
        ]

    def enable(self):
        """Enable the lighting system."""
        self._enabled = True

    def disable(self):
        """Disable the lighting system (no overlay rendered)."""
        self._enabled = False

    def clear_lights(self):
        """Remove all dynamic light sources (keep ambient torches)."""
        self.lights.clear()

    def add_light(self, x: int, y: int, radius: int = 200, color: tuple = _TORCH_COLOR,
                  intensity: float = 0.7, flicker: bool = False, pulse_speed: float = 0.0) -> LightSource:
        """Add a new light source to the scene.

        Args:
            x: X position on screen
            y: Y position on screen
            radius: Light radius in pixels
            color: RGB color tuple
            intensity: Base brightness (0.0 to 1.0)
            flicker: If True, apply torch-like flicker
            pulse_speed: Speed of gentle pulsing (0 = no pulse)

        Returns:
            The created LightSource (can be removed later)
        """
        light = LightSource(x, y, radius, color, intensity, flicker, pulse_speed)
        self.lights.append(light)
        return light

    def remove_light(self, light: LightSource):
        """Remove a previously added light source."""
        if light in self.lights:
            self.lights.remove(light)

    def set_status_effects(self, statuses: list):
        """Update the active status effects for status glow rendering.

        Args:
            statuses: List of status effect type strings (e.g., ["burning", "poisoned"])
        """
        self._status_effects = statuses

    def update_state(self, hp_ratio: float, madness: float, floor: int, max_floor: int,
                     in_combat: bool = False, enemy_hp_ratio: float = 1.0, is_boss: bool = False):
        """Update the lighting system with current game state.

        Args:
            hp_ratio: Player HP ratio (0.0 to 1.0)
            madness: Current madness value (0 to 100)
            floor: Current floor number
            max_floor: Maximum floor count
            in_combat: Whether the player is in combat
            enemy_hp_ratio: Enemy HP ratio for combat aura (0.0 to 1.0)
            is_boss: Whether the current enemy is a boss
        """
        self._hp_ratio = hp_ratio
        self._madness = madness
        self._floor = floor
        self._max_floor = max_floor
        self._in_combat = in_combat
        self._enemy_hp_ratio = enemy_hp_ratio
        self._boss = is_boss

    def _get_depth_params(self) -> dict:
        """Get lighting parameters based on current floor depth.

        Returns:
            Dict with ambient_alpha, torch_radius_mult, vignette_intensity
        """
        for (lo, hi), params in _DEPTH_DARKNESS.items():
            if lo <= self._floor <= hi:
                return {"ambient_alpha": params[0], "torch_mult": params[1],
                        "vig_int": params[2]}
        # Fallback for floors beyond defined ranges
        return {"ambient_alpha": 80, "torch_mult": 0.6, "vig_int": 0.55}

    def draw(self, surface: pygame.Surface, time_seconds: float):
        """Render the full lighting overlay onto the given surface.

        Composites all lighting layers onto the screen:
        1. Depth-based ambient darkness
        2. HP-based vignette
        3. Ambient torch light
        4. Status effect glows
        5. Dynamic light sources
        6. Boss eldritch pulsation

        Args:
            surface: The main display surface to render onto
            time_seconds: Total game time for animations
        """
        if not self._enabled:
            return

        self._overlay.fill((0, 0, 0, 0))

        depth = self._get_depth_params()

        # ── Layer 1: Depth-based ambient darkness ──
        if depth["ambient_alpha"] > 0:
            self._draw_ambient_darkness(depth["ambient_alpha"])

        # ── Layer 2: HP-based vignette ──
        self._draw_hp_vignette(time_seconds)

        # ── Layer 3: Ambient torch light sources ──
        for torch in self._ambient_torches:
            radius = int(torch.radius * depth["torch_mult"])
            intensity = torch.get_current_intensity(time_seconds)
            color = torch.get_current_color(time_seconds)
            self._draw_light_source(torch.x, torch.y, radius, color, intensity)

        # ── Layer 4: Status effect glows on screen edges ──
        self._draw_status_edge_glow(time_seconds)

        # ── Layer 5: Dynamic scene light sources ──
        for light in self.lights:
            intensity = light.get_current_intensity(time_seconds)
            color = light.get_current_color(time_seconds)
            self._draw_light_source(light.x, light.y, light.radius, color, intensity)

        # ── Layer 6: Boss eldritch pulsation ──
        if self._in_combat and self._boss:
            self._draw_boss_ambient_pulse(time_seconds)

        # ── Layer 7: Subtle ambient breathing ──
        self._draw_ambient_breathing(time_seconds, depth["ambient_alpha"])

        # Composite the overlay onto the screen
        surface.blit(self._overlay, (0, 0))

    def _draw_ambient_darkness(self, alpha: int):
        """Draw overall ambient darkness based on depth.

        Uses a large elliptical gradient to darken screen edges more than
        the center, creating the feeling of being deep underground where
        only the center of the screen is somewhat visible.
        """
        darkness = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        num_rings = 30
        max_rx = SCREEN_W // 2 + 100
        max_ry = SCREEN_H // 2 + 60
        for i in range(num_rings):
            ratio = i / num_rings
            # Quadratic falloff — edges much darker than center
            ring_alpha = int(alpha * ratio * ratio)
            if ring_alpha < 2:
                continue
            rx = int(max_rx * ratio)
            ry = int(max_ry * ratio)
            pygame.draw.ellipse(
                darkness,
                (8, 4, 16, ring_alpha),
                (SCREEN_W // 2 - rx, SCREEN_H // 2 - ry, rx * 2, ry * 2),
            )
        self._overlay.blit(darkness, (0, 0))

    def _draw_hp_vignette(self, time_seconds: float):
        """Draw a red-tinted vignette that intensifies as HP drops.

        The vignette has two components:
        - Edge darkness: always present but strengthens at low HP
        - Red pulse: a throbbing red tint that appears below 50% HP,
          pulsing faster as HP drops closer to zero

        This creates a visceral "danger" feeling that communicates the
        player's deteriorating condition without relying solely on the
        HP bar.
        """
        if self._hp_ratio >= 0.95:
            return  # No vignette at near-full HP

        # Base vignette intensity scales inversely with HP
        # 0% at full HP, up to 0.65 at 0 HP
        base_intensity = (1.0 - self._hp_ratio) * 0.65

        # Pulse speed increases as HP drops (more urgent)
        pulse_speed = 1.0 + (1.0 - self._hp_ratio) * 3.0
        pulse = 0.5 + 0.5 * math.sin(time_seconds * pulse_speed)

        # Pulsed intensity: base + pulse component
        pulsed = base_intensity * (0.75 + 0.25 * pulse)

        # Red channel intensifies at low HP
        red_factor = max(0, 1.0 - self._hp_ratio * 1.5)  # 0 at 66%+, 1.0 at 0%
        r = int(50 * red_factor)
        g = 0
        b = int(10 * red_factor * 0.3)

        vignette = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        num_rings = 40
        max_rx = SCREEN_W // 2 + 80
        max_ry = SCREEN_H // 2 + 50
        for i in range(num_rings):
            ratio = i / num_rings
            alpha = int(255 * pulsed * ratio * ratio)
            if alpha < 3:
                continue
            rx = int(max_rx * ratio)
            ry = int(max_ry * ratio)
            pygame.draw.ellipse(
                vignette,
                (r, g, b, min(255, alpha)),
                (SCREEN_W // 2 - rx, SCREEN_H // 2 - ry, rx * 2, ry * 2),
            )
        self._overlay.blit(vignette, (0, 0))

    def _draw_status_edge_glow(self, time_seconds: float):
        """Draw colored glow on screen edges based on active status effects.

        When the player has status effects like burning or poisoned, a subtle
        colored light bleeds in from the screen edges, reinforcing the feeling
        of being affected. The glow is more intense with more severe statuses
        and pulses gently to draw attention.

        Each status type maps to a specific color:
        - Burning: fierce orange edges
        - Poisoned: sickly green tinge at bottom
        - Bleeding: crimson drip from top
        - Freezing: icy blue frost at bottom edges
        - Doom: dark magenta pulse
        """
        if not self._status_effects:
            return

        for status in self._status_effects:
            color = _STATUS_GLOW_COLORS.get(status)
            if color is None:
                continue

            pulse = 0.5 + 0.5 * math.sin(time_seconds * 1.5 + hash(status) % 100)
            alpha = int(25 + 35 * pulse)

            glow = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

            # Different edge emphasis per status type
            if status == "burning":
                # Fire glow from all edges
                for i in range(20):
                    a = int(alpha * (1 - i / 20))
                    pygame.draw.rect(glow, (*color, a), (i, i, SCREEN_W - i * 2, SCREEN_H - i * 2), 1)
            elif status == "poisoned":
                # Green creeping up from bottom
                for i in range(30):
                    a = int(alpha * (1 - i / 30))
                    pygame.draw.line(glow, (*color, a), (0, SCREEN_H - 1 - i), (SCREEN_W, SCREEN_H - 1 - i))
                    # Subtle side bleed
                    if i < 15:
                        pygame.draw.line(glow, (*color, a // 2), (i, SCREEN_H - i), (i, SCREEN_H))
                        pygame.draw.line(glow, (*color, a // 2), (SCREEN_W - 1 - i, SCREEN_H - i),
                                         (SCREEN_W - 1 - i, SCREEN_H))
            elif status == "bleeding":
                # Red dripping from top
                for i in range(25):
                    a = int(alpha * (1 - i / 25))
                    pygame.draw.line(glow, (*color, a), (0, i), (SCREEN_W, i))
            elif status == "freezing":
                # Ice blue frost at bottom corners
                for i in range(20):
                    a = int(alpha * (1 - i / 20))
                    pygame.draw.line(glow, (*color, a), (0, SCREEN_H - 1 - i), (SCREEN_W, SCREEN_H - 1 - i))
                    pygame.draw.line(glow, (*color, a // 3), (0, i), (SCREEN_W, i))
            elif status == "doom":
                # Pulsing magenta vignette
                for i in range(25):
                    ratio = i / 25
                    a = int(alpha * 1.5 * ratio * ratio)
                    pygame.draw.rect(glow, (*color, min(255, a)),
                                     (i * 3, i * 3, SCREEN_W - i * 6, SCREEN_H - i * 6), 1)
            else:
                # Generic: subtle full edge glow
                for i in range(15):
                    a = int(alpha * 0.7 * (1 - i / 15))
                    pygame.draw.rect(glow, (*color, a), (i, i, SCREEN_W - i * 2, SCREEN_H - i * 2), 1)

            self._overlay.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_light_source(self, x: int, y: int, radius: int, color: tuple, intensity: float):
        """Draw a single light source as an additive glow.

        Uses a cached radial gradient texture centered at the given position.
        The texture is blitted with additive blending (BLEND_RGBA_ADD) so
        overlapping lights naturally combine to create brighter areas.

        Args:
            x: Center X position
            y: Center Y position
            radius: Light radius in pixels
            color: RGB color of the light
            intensity: Current brightness (0.0 to 1.0)
        """
        if intensity < 0.05 or radius < 10:
            return
        texture = _get_light_texture(radius, color, intensity)
        self._overlay.blit(texture, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_boss_ambient_pulse(self, time_seconds: float):
        """Draw an ambient eldritch pulse during boss fights.

        During boss encounters, a subtle purple/magenta pulsation bleeds
        in from the screen edges, synchronized with a slow, heavy rhythm
        that evokes the oppressive presence of a cosmic horror. The
        intensity increases as the boss loses HP, suggesting the entity
        is becoming more desperate and reality is thinning.

        The pulse uses two overlapping sine waves at different frequencies
        to create an irregular, unsettling rhythm that never quite repeats.
        """
        # Intensity increases as boss HP drops
        boss_intensity = 0.3 + (1.0 - self._enemy_hp_ratio) * 0.7

        # Irregular dual-frequency pulse for unsettling rhythm
        pulse1 = 0.5 + 0.5 * math.sin(time_seconds * 0.7)
        pulse2 = 0.5 + 0.5 * math.sin(time_seconds * 1.3 + 1.0)
        combined_pulse = (pulse1 * 0.6 + pulse2 * 0.4) * boss_intensity

        if combined_pulse < 0.1:
            return

        # Eldritch purple-magenta color
        r = int(60 * combined_pulse)
        g = int(15 * combined_pulse)
        b = int(80 * combined_pulse)

        pulse_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        num_rings = 20
        for i in range(num_rings):
            ratio = i / num_rings
            alpha = int(40 * combined_pulse * ratio * ratio)
            if alpha < 2:
                continue
            rx = int((SCREEN_W // 2 + 100) * ratio)
            ry = int((SCREEN_H // 2 + 60) * ratio)
            pygame.draw.ellipse(
                pulse_surf,
                (r, g, b, alpha),
                (SCREEN_W // 2 - rx, SCREEN_H // 2 - ry, rx * 2, ry * 2),
            )
        self._overlay.blit(pulse_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_ambient_breathing(self, time_seconds: float, depth_alpha: int):
        """Draw a subtle overall light/dark breathing cycle.

        Creates a very slow, barely perceptible oscillation in overall
        brightness that adds to the feeling of unease. The player may
        not consciously notice it, but it contributes to the oppressive
        atmosphere. The breathing is faster at deeper dungeon levels.

        Args:
            time_seconds: Total game time for animation
            depth_alpha: Base ambient darkness alpha from depth params
        """
        if depth_alpha < 10:
            return  # No breathing on well-lit floors

        # Very slow breathing (12-second cycle at floor 1, 6-second at floor 20)
        breath_period = max(6.0, 12.0 - self._floor * 0.3)
        breath = 0.5 + 0.5 * math.sin(time_seconds * (math.tau / breath_period))

        # Subtle alpha modulation: +/- 15% of depth darkness
        mod = int(depth_alpha * 0.15 * (breath - 0.5))
        if abs(mod) < 2:
            return

        breath_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        if mod > 0:
            # Darken slightly
            breath_surf.fill((5, 2, 10, mod))
        else:
            # Lighten slightly (reduce darkness)
            breath_surf.fill((0, 0, 0, 0))  # Can't "subtract" alpha easily, skip lightening

        if mod > 0:
            self._overlay.blit(breath_surf, (0, 0))


# ═══════════════════════════════════════════
# CONVENIENCE FUNCTIONS FOR SCREEN INTEGRATION
# ═══════════════════════════════════════════

def create_combat_lighting(player_x: int, player_y: int, enemy_x: int, enemy_y: int,
                           player_statuses: list = None) -> list:
    """Create standard combat light sources.

    Returns a list of LightSource objects appropriate for a combat screen:
    - Warm torch light behind the player
    - Subtle light behind the enemy
    - Central combat area illumination

    Args:
        player_x: Player sprite center X
        player_y: Player sprite center Y
        enemy_x: Enemy sprite center X
        enemy_y: Enemy sprite center Y
        player_statuses: List of active status effect strings

    Returns:
        List of LightSource objects
    """
    lights = []

    # Player torch — warm, flickering, medium radius
    lights.append(LightSource(
        player_x, player_y + 40, radius=220,
        color=_TORCH_COLOR, intensity=0.5, flicker=True
    ))

    # Enemy light — cooler, more distant
    enemy_color = (180, 140, 200)  # Cold purple for enemies
    lights.append(LightSource(
        enemy_x, enemy_y + 30, radius=180,
        color=enemy_color, intensity=0.3, pulse_speed=1.5
    ))

    # Center combat area — neutral ambient
    center_x = (player_x + enemy_x) // 2
    center_y = (player_y + enemy_y) // 2
    lights.append(LightSource(
        center_x, center_y, radius=300,
        color=(180, 160, 130), intensity=0.15
    ))

    # Status effect glows
    if player_statuses:
        for status in player_statuses:
            color = _STATUS_GLOW_COLORS.get(status)
            if color:
                lights.append(LightSource(
                    player_x, player_y, radius=150,
                    color=color, intensity=0.25, pulse_speed=2.0
                ))

    return lights
