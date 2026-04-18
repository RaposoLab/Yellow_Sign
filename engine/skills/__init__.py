"""Skill handler system: heal/shield/buff registries and player skill dispatch.

This package replaces the former monolithic `engine/skills.py` with a clean
modular structure:

    _types.py   — Shared type aliases (LogEntry, HealCalcFn, etc.)
    heal.py     — Heal calculation functions + HEAL_HANDLERS + dispatcher
    shield.py   — Shield calculation functions + SHIELD_HANDLERS + dispatcher
    buff.py     — Buff handler functions + BUFF_HANDLERS + message templates + dispatcher
    dispatch.py — player_use_skill (main skill usage orchestrator)

All public symbols are re-exported here for backward compatibility:
    from engine.skills import player_use_skill, HEAL_HANDLERS, ...
"""

# Type aliases
from engine.skills._types import LogEntry, HealCalcFn, ShieldCalcFn, BuffApplyFn

# Heal system
from engine.skills.heal import HEAL_HANDLERS, _handle_self_heal, _calc_heal_default

# Shield system
from engine.skills.shield import SHIELD_HANDLERS, _handle_self_shield

# Buff system
from engine.skills.buff import BUFF_HANDLERS, _BUFF_MESSAGES, _handle_self_buff

# Main dispatcher
from engine.skills.dispatch import player_use_skill

__all__ = [
    # Types
    "LogEntry",
    "HealCalcFn",
    "ShieldCalcFn",
    "BuffApplyFn",
    # Heal
    "HEAL_HANDLERS",
    "_handle_self_heal",
    "_calc_heal_default",
    # Shield
    "SHIELD_HANDLERS",
    "_handle_self_shield",
    # Buff
    "BUFF_HANDLERS",
    "_BUFF_MESSAGES",
    "_handle_self_buff",
    # Dispatch
    "player_use_skill",
]
