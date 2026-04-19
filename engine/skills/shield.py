"""Shield handler functions and registry.

10 shield calculation functions + SHIELD_HANDLERS registry + _handle_self_shield dispatcher.
"""

from typing import List, Dict, Tuple, Optional

from data import MADNESS_MAX, MAX_BARRIER_STACKS
from engine.models import Skill, GameState
from engine.skills._types import LogEntry, ShieldCalcFn

# ═══════════════════════════════════════════
# SHIELD CALCULATION FUNCTIONS
# ═══════════════════════════════════════════


def _shield_int2_wis1(state: GameState, skill: Skill) -> int:
    """Calculate shield as 2x INT + WIS."""
    return int(state.stats["int"] * 2 + state.stats["wis"])


def _shield_wis3_int1(state: GameState, skill: Skill) -> int:
    """Calculate shield as 3x WIS + 1.5x INT."""
    return int(state.stats["wis"] * 3 + state.stats["int"] * 1.5)


def _shield_wis3_hits(state: GameState, skill: Skill) -> int:
    """Calculate shield as 3x WIS + 5x hits taken.

    Scales with damage taken — the more punishment absorbed, the stronger
    the ward becomes, rewarding aggressive play under pressure.
    """
    return int(state.stats["wis"] * 3 + state.hits_taken * 5)


def _shield_sanctuary(state: GameState, skill: Skill) -> int:
    """Sanctuary: adds 3 barrier stacks, heals 2x WIS, returns 4x WIS shield.

    A powerful defensive cooldown that simultaneously bolsters the player
    with barriers, healing, and a stat-scaled shield value.
    """
    state.barrier = min(MAX_BARRIER_STACKS, state.barrier + 3)
    h = int(state.stats["wis"] * 2)
    state.hp = min(state.max_hp, state.hp + h)
    return int(state.stats["wis"] * 4)


def _shield_glyph_1(state: GameState, skill: Skill) -> Optional[int]:
    """Warding Glyph: adds 1 barrier stack, no direct shield value.

    Returns None because barrier stacks handle the absorption; the glyph
    itself doesn't contribute a numeric shield amount.
    """
    state.barrier = min(MAX_BARRIER_STACKS, state.barrier + 1)
    return None


def _shield_fracSan(state: GameState, skill: Skill) -> int:
    """Fractured Sanity: 3x INT shield, adds 10 madness.

    Trading mental stability for raw arcane protection — the shield
    grows with INT but at the cost of significant madness.
    """
    state.madness = min(MADNESS_MAX, state.madness + 10)
    return int(state.stats["int"] * 3)


def _shield_str3_hits(state: GameState, skill: Skill) -> int:
    """Bone Armor: 3x STR + 5x hits taken shield.

    A brute-force defensive skill that scales with physical strength
    and accumulated damage, ideal for warriors who absorb punishment.
    """
    return int(state.stats.get("str", 10) * 3 + state.hits_taken * 5)


def _shield_madShell(state: GameState, skill: Skill) -> int:
    """Madness Shell: 2x WIS + madness shield, adds 10 madness.

    Shield is calculated BEFORE adding madness so the value reflects
    the player's current madness state, not the post-cost madness.
    """
    shield_val = int(state.stats["wis"] * 2 + state.madness)
    state.madness = min(MADNESS_MAX, state.madness + 10)
    return shield_val


def _shield_madBarrier(state: GameState, skill: Skill) -> int:
    """Madness Barrier: 3x WIS + 2x LUCK shield."""
    return int(state.stats["wis"] * 3 + state.luck * 2)


def _shield_madEndur(state: GameState, skill: Skill) -> int:
    """Madman's Endurance: 2x WIS shield, regen buff, adds 8 madness.

    A sustainable defensive skill that provides ongoing regeneration
    alongside the immediate shield, at a moderate madness cost.
    """
    state.madness = min(MADNESS_MAX, state.madness + 8)
    state.buffs["regen"] = 2
    return int(state.stats["wis"] * 2)


# ═══════════════════════════════════════════
# SHIELD HANDLER REGISTRY
# ═══════════════════════════════════════════

SHIELD_HANDLERS: Dict[str, Tuple[ShieldCalcFn, str]] = {
    "int2_wis1": (_shield_int2_wis1, "Psychic Shield: {v} damage absorbed!"),
    "wis3_int1": (_shield_wis3_int1, "Aegis Shield: {v} damage absorbed!"),
    "wis3_hits": (_shield_wis3_hits, "Eldritch Ward: {v} shield!"),
    "sanctuary": (_shield_sanctuary, "Sanctuary! Barrier x3, Shield {v}, Heal {h}!"),
    "glyph_1": (
        _shield_glyph_1,
        "Warding Glyph! Barrier absorbs next hit! ({v} stacks)",
    ),
    "fracSan": (_shield_fracSan, "Fractured Sanity! Shield {v}! (+10 MAD)"),
    "str3_hits": (_shield_str3_hits, "Bone Armor: {v} shield!"),
    "madShell": (_shield_madShell, "Madness Shell: {v} shield! (+10 MAD)"),
    "madBarrier": (_shield_madBarrier, "Madness Barrier: {v} shield!"),
    "madEndur": (
        _shield_madEndur,
        "Madman's Endurance! Shield {v}, regen 5%! (+8 MAD)",
    ),
}


# ═══════════════════════════════════════════
# SHIELD DISPATCHER
# ═══════════════════════════════════════════


def _handle_self_shield(state: GameState, skill: Skill) -> List[LogEntry]:
    """Handle self_shield skill type. Returns list of log messages."""
    handler, msg_template = SHIELD_HANDLERS.get(skill.shield_calc or "", (None, None))
    if handler is None or msg_template is None:
        return [(f"{skill.name} activated!", "shield")]

    result = handler(state, skill)
    if result is not None:
        state.shield = result

    h = int(state.stats["wis"] * 2) if skill.shield_calc == "sanctuary" else 0
    v = state.barrier if skill.shield_calc == "glyph_1" else (result or state.shield)
    msg = msg_template.format(v=v, h=h)
    return [(msg, "shield")]
