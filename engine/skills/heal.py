"""Heal handler functions and registry.

15 heal calculation functions + HEAL_HANDLERS registry + _handle_self_heal dispatcher.
"""

from typing import List, Dict, Tuple

from data import MADNESS_MAX
from engine.models import Skill, GameState
from engine.skills._types import LogEntry, HealCalcFn

# ═══════════════════════════════════════════
# HEAL CALCULATION FUNCTIONS
# ═══════════════════════════════════════════


def _calc_heal_int2_buff(state: GameState, skill: Skill) -> int:
    """Calculate healing for Forbidden Knowledge skill.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Increases base INT by 3 and recalculates stats
    """
    h = int(state.stats["int"] * 2)
    state.base_stats["int"] += 3
    state.recalc_stats()
    return h


def _calc_heal_missing_hp(state: GameState, skill: Skill) -> int:
    """Calculate healing based on missing HP percentage.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed (60% of missing HP)
    """
    if state.max_hp <= 0:
        return 0
    missing = 1 - state.hp / state.max_hp
    return int(missing * state.max_hp * 0.6)


def _calc_heal_wis2_10(state: GameState, skill: Skill) -> int:
    """Calculate healing as 2x WIS + 10.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed
    """
    return int(state.stats["wis"] * 2) + 10


def _calc_heal_wis3_int1(state: GameState, skill: Skill) -> int:
    """Calculate healing as 3x WIS + 1.5x INT.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed
    """
    return int(state.stats["wis"] * 3 + state.stats["int"] * 1.5)


def _calc_heal_wis2_luck1(state: GameState, skill: Skill) -> int:
    """Calculate healing as 2.5x WIS + LUCK, adds 5 madness.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Increases madness by 5
    """
    h = int(state.stats["wis"] * 2.5 + state.luck * 1)
    state.madness = min(MADNESS_MAX, state.madness + 5)
    return h


def _calc_heal_full_heal(state: GameState, skill: Skill) -> int:
    """Full heal that restores HP to max, adds 25 madness.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        0 (healing handled directly via side effect)

    Side Effects:
        Sets HP to max, increases madness by 25
    """
    state.hp = state.max_hp
    state.madness = min(MADNESS_MAX, state.madness + 25)
    return 0


def _calc_heal_int2_mend(state: GameState, skill: Skill) -> int:
    """Calculate healing as 2x INT.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed
    """
    return int(state.stats["int"] * 2)


def _calc_heal_devour15(state: GameState, skill: Skill) -> int:
    """Calculate healing as 15% of max HP.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed
    """
    return int(state.max_hp * 0.15)


def _calc_heal_titanResil(state: GameState, skill: Skill) -> int:
    """Calculate healing as 40% of max HP, cleanses all debuffs.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Clears all status effects
    """
    state.statuses.clear()
    return int(state.max_hp * 0.40)


def _calc_heal_layOnHands(state: GameState, skill: Skill) -> int:
    """Calculate healing as 3x WIS, cleanses all debuffs.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Clears all status effects
    """
    state.statuses.clear()
    return int(state.stats["wis"] * 3)


def _calc_heal_meditation(state: GameState, skill: Skill) -> int:
    """Calculate healing as 20% of max HP, reduces madness by 10.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Reduces madness by 10
    """
    state.madness = max(0, state.madness - 10)
    return int(state.max_hp * 0.20)


def _calc_heal_darkRegen(state: GameState, skill: Skill) -> int:
    """Calculate healing as 30% of max HP, adds dark regen buff.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Adds darkRegenBuff for 2 turns
    """
    state.buffs["darkRegenBuff"] = 2
    return int(state.max_hp * 0.30)


def _calc_heal_hasturEmbrace(state: GameState, skill: Skill) -> int:
    """Full heal with immunity buff, adds 20 madness.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        0 (healing handled directly via side effect)

    Side Effects:
        Sets HP to max, adds immunity buff for 2 turns, increases madness by 20
    """
    state.hp = state.max_hp
    state.madness = min(MADNESS_MAX, state.madness + 20)
    state.buffs["immunity"] = 2
    return 0


def _calc_heal_secondWind(state: GameState, skill: Skill) -> int:
    """Calculate healing as 20% of max HP, adds regen buff.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Adds regen buff for 2 turns
    """
    state.buffs["regen"] = 2
    return int(state.max_hp * 0.20)


def _calc_heal_nimbleRecov(state: GameState, skill: Skill) -> int:
    """Calculate healing as 25% of max HP, adds evasion buff.

    Args:
        state: Current game state
        skill: Skill being used (unused for this calculation)

    Returns:
        Amount of HP healed

    Side Effects:
        Adds evasionUp buff for 2 turns
    """
    state.buffs["evasionUp"] = 2
    return int(state.max_hp * 0.25)


def _calc_heal_default(state: GameState, skill: Skill) -> int:
    """Default healing calculation as 2x specified stat.

    Args:
        state: Current game state
        skill: Skill containing stat to use for calculation

    Returns:
        Amount of HP healed (defaults to 20 if stat not found)
    """
    return int(state.stats.get(skill.stat, 10) * 2)


# ═══════════════════════════════════════════
# HEAL HANDLER REGISTRY
# ═══════════════════════════════════════════

# Heal handler registry: heal_calc name -> (calc_fn, message)
HEAL_HANDLERS: Dict[str, Tuple[HealCalcFn, str]] = {
    "int2_buff": (_calc_heal_int2_buff, "Forbidden Knowledge heals {h} HP! INT+3!"),
    "missing_hp": (_calc_heal_missing_hp, "Adrenaline Surge heals {h} HP!"),
    "wis2_10": (_calc_heal_wis2_10, "Purifying Touch heals {h} HP!"),
    "wis3_int1_heal": (_calc_heal_wis3_int1, "Healing Light restores {h} HP!"),
    "wis2_luck1": (_calc_heal_wis2_luck1, "Laughing heals {h} HP! (+5 MAD)"),
    "full_heal": (_calc_heal_full_heal, "Carcosa's Blessing: Full heal! (+25 MAD)"),
    "int2_mend": (_calc_heal_int2_mend, "Abyssal Mend heals {h} HP!"),
    "devour15": (_calc_heal_devour15, "Devour heals {h} HP!"),
    "titanResil": (
        _calc_heal_titanResil,
        "Titanic Resilience heals {h} HP and cleanses all debuffs!",
    ),
    "layOnHands": (_calc_heal_layOnHands, "Lay on Hands heals {h} HP and cleanses!"),
    "meditation": (_calc_heal_meditation, "Blessed Meditation heals {h} HP! -10 MAD!"),
    "darkRegen": (_calc_heal_darkRegen, "Dark Regeneration heals {h} HP! EVA+20% 2t!"),
    "hasturEmbrace": (
        _calc_heal_hasturEmbrace,
        "Hastur's Embrace: Full heal! Immune debuffs 2t! (+20 MAD)",
    ),
    "secondWind": (_calc_heal_secondWind, "Second Wind heals {h} HP! Regen 3% 2t!"),
    "nimbleRecov": (
        _calc_heal_nimbleRecov,
        "Nimble Recovery heals {h} HP! EVA+15% 2t!",
    ),
}


# ═══════════════════════════════════════════
# HEAL DISPATCHER
# ═══════════════════════════════════════════


def _handle_self_heal(state: GameState, skill: Skill) -> List[LogEntry]:
    """Handle self_heal skill type. Returns list of log messages.

    Note: Some heal handlers (full_heal, hasturEmbrace) return 0 because they
    set HP directly as a side effect. The message template is always formatted
    so those handlers can display their special text (e.g. 'Full heal!').
    """
    calc_fn, msg_template = HEAL_HANDLERS.get(skill.heal_calc or "", (_calc_heal_default, "Recovered {h} HP!"))
    h = calc_fn(state, skill)
    if h > 0:
        state.hp = min(state.max_hp, state.hp + h)
    # Always format the template — handlers that set HP directly still
    # produce meaningful messages even when h == 0.
    msg = msg_template.format(h=h)
    return [(msg, "heal")]
