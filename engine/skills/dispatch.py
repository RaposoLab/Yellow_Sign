"""Player skill dispatch: cooldowns, costs, damage, and effect application.

This module contains the main `player_use_skill` function that orchestrates
skill usage — from pre-checks (cooldown, madness cost, HP cost) through
damage calculation to post-effect processing (lifesteal, status effects,
random Hastur effects, etc.).
"""

import random
from typing import List

from data import MADNESS_MAX, POISON_MAX_STACKS
from engine.models import Skill, GameState, apply_status
from engine.skills._types import LogEntry
from engine.skills.heal import _handle_self_heal
from engine.skills.shield import _handle_self_shield
from engine.skills.buff import _handle_self_buff


def player_use_skill(state: GameState, skill_index: int) -> List[LogEntry]:
    """Player uses a skill. Returns list of (text, type) log messages.

    Flow:
        1. Pre-checks (cooldown, madness cost, HP cost)
        2. Route to non-damage handler if self_heal / self_shield / self_buff
        3. Accuracy check for damage skills
        4. Damage calculation, application, and lifesteal
        5. Post-effect processing (ethereal consume, Living Shadow, statuses)
    """
    from engine.combat import calc_player_damage, apply_damage_to_enemy

    logs: List[LogEntry] = []
    skill = state.active_skills[skill_index]
    c = state.combat
    e = c.enemy

    # --- Pre-checks ---
    if skill.current_cd > 0:
        return [("That ability is on cooldown!", "info")]

    if skill.cost > 0:
        state.madness = min(MADNESS_MAX, state.madness + skill.cost)
        if state.madness >= MADNESS_MAX:
            return [("Your mind shatters from the madness cost!", "damage")]

    if skill.madness_cost > 0:
        state.madness = max(0, state.madness - skill.madness_cost)

    if skill.hp_cost > 0:
        hp_loss = int(state.max_hp * skill.hp_cost)
        state.hp = max(1, state.hp - hp_loss)
        logs.append((f"Sacrificed {hp_loss} HP!", "damage"))

    skill.current_cd = skill.cd + 1

    # --- Non-damage skill types ---
    if skill.type == "self_heal":
        return logs + _handle_self_heal(state, skill)

    if skill.type == "self_shield":
        return logs + _handle_self_shield(state, skill)

    if skill.type == "self_buff":
        return logs + _handle_self_buff(state, skill)

    # Accuracy miss check (skip for true_strike skills)
    if not skill.true_strike:
        if random.random() * 100 >= state.accuracy:
            logs.append((f"{skill.name} misses!", "info"))
            return logs

    # Damage-dealing skill
    raw = calc_player_damage(state, skill)

    if skill.consume_shield:
        raw += state.shield
        state.shield = 0
        logs.append(("Shield consumed for extra damage!", "effect"))

    if skill.shield_scaling:
        raw += int(state.shield * skill.shield_scaling)

    dmg, is_crit = apply_damage_to_enemy(state, raw, skill)
    crit_text = " CRITICAL!" if is_crit else ""
    logs.append(
        (
            f"You use {skill.name} for {dmg} damage!{crit_text}",
            "crit" if is_crit else "damage",
        )
    )

    if skill.lifesteal and dmg > 0:
        h = int(dmg * skill.lifesteal)
        state.hp = min(state.max_hp, state.hp + h)
        logs.append((f"Stole {h} HP!", "heal"))

    # Consume ethereal buff after attack
    if state.buffs.get("ethereal", 0) > 0 and dmg > 0:
        state.buffs["ethereal"] = 0

    # Living Shadow: copy enemy's last attack as bonus damage
    if state.buffs.get("copyAttack", 0) > 0 and c.last_enemy_skill and dmg > 0:
        copied = c.last_enemy_skill
        copied_power = copied.get("power", 1.0)
        copy_dmg = int(state.atk * copied_power * 0.5)
        e.hp = max(0, e.hp - copy_dmg)
        logs.append(
            (
                f"Living Shadow copies {copied.get('name', 'attack')} for {copy_dmg}!",
                "damage",
            )
        )

    if state.madness >= MADNESS_MAX:
        return logs + [("Your mind shatters from the madness!", "damage")]

    # Apply effects
    if skill.effect:
        apply_status(e, skill.effect, skill.duration)
        if skill.effect == "poisoned":
            existing = next((s for s in e.statuses if s.type == "poisoned"), None)
            if existing:
                existing.stacks = min(POISON_MAX_STACKS, existing.stacks + 1)
        logs.append((f"{skill.effect} applied to {e.name}!", "effect"))

    if skill.effect2:
        apply_status(e, skill.effect2, skill.duration)
        logs.append((f"{skill.effect2} applied to {e.name}!", "effect"))

    if skill.effect3:
        apply_status(e, skill.effect3, skill.duration)
        logs.append((f"{skill.effect3} applied to {e.name}!", "effect"))

    if skill.extend_debuffs:
        for st in e.statuses:
            st.duration += 2
        if e.statuses:
            logs.append(("All debuffs extended by 2 turns!", "effect"))

    if skill.random_effect:
        choice = random.randint(0, 3)
        if choice == 0:
            h = int(state.max_hp * 0.5)
            state.hp = min(state.max_hp, state.hp + h)
            logs.append((f"Hastur heals you for {h}!", "heal"))
        elif choice == 1:
            for eff in ("burning", "petrified", "blinded", "shocked", "poisoned"):
                apply_status(e, eff, 3)
            logs.append(("Hastur curses your foe with ALL debuffs!", "effect"))
        elif choice == 2:
            raw2 = int((5 + state.stats["wis"] * 2.0) * 3.0)
            dmg2, _ = apply_damage_to_enemy(state, raw2, skill)
            logs.append((f"Hastur smites for {dmg2}!", "crit"))
        else:
            state.base_stats["luck"] = state.base_stats.get("luck", 5) + 5
            state.recalc_stats()
            logs.append(("Hastur grants LUK+5!", "effect"))

    return logs
