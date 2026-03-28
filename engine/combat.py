"""Combat system: damage calculation, status effects, enemy AI."""

import random
import math
from typing import List, Tuple, Optional, Dict, Any

from data import (
    ENEMIES, BOSS,
    DEFENSE_DENOM, CRIT_BASE_MULT,
    DMG_VARIANCE_LOW, DMG_VARIANCE_RANGE, LUCK_DMG_VARIANCE,
    ENEMY_VAR_LOW, ENEMY_VAR_RANGE,
    FLEE_BASE_CHANCE, FLEE_AGI_MULTIPLIER, FLEE_SUCCESS_MADNESS, FLEE_FAIL_MADNESS,
    EXECUTE_HP_THRESHOLD, EXECUTE_DAMAGE_MULT,
    COIN_FLIP_HEAL_FRAC, COIN_FLIP_DAMAGE_MULT, GAMBLE_MIN, GAMBLE_RANGE,
    DOOM_HP_THRESHOLD,
    BOSS_PHASE2_HP, BOSS_PHASE3_HP, BOSS_PHASE3_ATK_MULT,
    BURNING_HP_PCT, POISON_HP_PCT, BLEEDING_HP_PCT, POISON_MAX_STACKS,
    FREEZING_PHYS_MULT, PETRIFIED_MAGIC_MULT, WEAKENED_ATK_MULT, WEAKENED_DEF_MULT,
    SHOCK_STUN_CHANCE, BLIND_MISS_CHANCE,
    REGEN_HP_PCT, REGEN5_HP_PCT, OATH_HP_PCT,
    DAMAGE_BUFF_MULTIPLIERS, DEFENSE_BUFF_TABLE, EVASION_BUFF_TABLE,
    MIRROR_IMG_REDUCTION, BLOOD_AURA_LS_PCT, RETRIB_AURA_REFLECT_PCT,
    DREADNOUGHT_CONVERSION_PCT, ELDRITCH_REBIRTH_HP_PCT,
    CRIT_UP_BONUS, ATK_CRIT_UP_BONUS,
    XP_BASE, XP_PER_FLOOR, XP_BOSS_BONUS,
    GOLD_BASE, GOLD_PER_FLOOR, GOLD_BOSS_BONUS, GOLD_BASE_RANDOM_MAX,
    MADNESS_BOSS_KILL, MADNESS_NORMAL_KILL, STAT_KEYS,
)
from engine.models import Item, Skill, StatusEffect, Enemy, CombatState, GameState, has_status, apply_status
from engine.items import generate_item
from engine.skills import player_use_skill


# ═══════════════════════════════════════════
# COMBAT SYSTEM
# ═══════════════════════════════════════════

def start_combat(state: GameState, is_boss: bool = False) -> None:
    """Initialize a combat encounter."""
    if is_boss or state.floor >= state.max_floor:
        ed = dict(BOSS)
    else:
        pool = [e for e in ENEMIES if e["level_range"][0] <= state.floor <= e["level_range"][1]]
        ed = dict(random.choice(pool)) if pool else dict(ENEMIES[0])

    enemy = Enemy(ed, state.floor)
    state.combat = CombatState(enemy, is_boss)
    state.shield = 0
    state.barrier = 0
    state.rage = False
    state.buffs = {}
    state.temp_stats = {}
    state.hits_taken = 0
    for sk in state.active_skills:
        sk.current_cd = 0
    state.combat.add_log(f"{enemy.name} appears!", "info")
    if enemy.desc:
        state.combat.add_log(enemy.desc, "info")


def _base_damage(state: GameState, skill: Skill) -> float:
    """Core damage calculation shared by player and preview paths.
    Returns raw base damage as float (no random variance, no defense reduction).
    """
    sv = state.stats.get(skill.stat, 10)
    s2v = state.stats.get(skill.stat2, 10) if skill.stat2 else 0

    if skill.type in ("physical", "physical_debuff", "mixed_phys"):
        bd = state.atk * (skill.power or 1) + sv * 0.8
        if skill.stat2_mult:
            bd += s2v * skill.stat2_mult
        if skill.def_scaling:
            bd += state.defense * 1.0
    elif skill.type in ("magic", "magic_debuff", "mixed_magic"):
        bd = (5 + sv * 1.5) * (skill.power or 1)
        if skill.stat2_mult:
            bd += s2v * skill.stat2_mult
    elif skill.type == "debuff":
        bd = (5 + sv * 1.5) * (skill.power or 1)
    elif skill.type in ("self_buff", "self_heal", "self_shield", "curse", "ultimate"):
        bd = 0
        if skill.type == "curse" and skill.consume_shield:
            bd = (5 + sv * 1.5) * skill.power + state.shield
        elif skill.type == "ultimate":
            bd = (5 + sv * 1.5) * skill.power
            if skill.stat2_mult:
                bd += s2v * skill.stat2_mult
        else:
            bd = (5 + sv * 1.5) * (skill.power or 1) if skill.power else 0
    else:
        bd = (5 + sv * 1.5) * (skill.power or 1)

    if skill.scaling_low_hp:
        hr = state.hp / state.max_hp
        bd *= 1 + (1 - hr) * 2.0

    if skill.madness_scaling:
        bd *= (1 + state.madness / 100)

    # Apply damage buff multipliers from registry
    for buff_key, mult in DAMAGE_BUFF_MULTIPLIERS.items():
        if state.buffs.get(buff_key, 0) > 0:
            bd *= mult

    if skill.multihit and skill.multihit > 1:
        bd *= skill.multihit

    if skill.execute_bonus and state.combat:
        e = state.combat.enemy
        if e and e.hp / e.max_hp < EXECUTE_HP_THRESHOLD:
            bd *= EXECUTE_DAMAGE_MULT

    if skill.luck_bonus:
        bd *= (1 + state.luck * 0.02)

    return bd


def calc_player_damage(state: GameState, skill: Skill) -> int:
    """Calculate raw player damage for a skill (with random variance)."""
    bd = _base_damage(state, skill)

    # Random variance
    bd *= (1 + random.random() * state.luck * LUCK_DMG_VARIANCE)
    bd *= (DMG_VARIANCE_LOW + random.random() * DMG_VARIANCE_RANGE)

    if skill.gamble:
        gm = GAMBLE_MIN + random.random() * GAMBLE_RANGE
        bd *= gm

    if skill.coin_flip:
        if random.random() < 0.5:
            bd = 0
            h = int(state.max_hp * COIN_FLIP_HEAL_FRAC)
            state.hp = min(state.max_hp, state.hp + h)
        else:
            bd *= COIN_FLIP_DAMAGE_MULT

    return int(bd)


def calc_preview_damage(state: GameState, skill: Skill) -> Tuple[int, int]:
    """Calculate deterministic preview damage for a skill (no random variance).
    Returns (base_dmg, final_dmg_after_def) as approximate range center.
    """
    bd = _base_damage(state, skill)

    base_dmg = int(bd)
    if base_dmg <= 0:
        return 0, 0

    # Apply enemy defense reduction
    final_dmg = base_dmg
    if state.combat and state.combat.enemy:
        e = state.combat.enemy
        df = e.defense
        if skill.type in ("magic", "magic_debuff", "mixed_magic"):
            df = e.m_def
        if skill.armor_pierce:
            df *= (1 - skill.armor_pierce)
        if has_status(e, "weakened"):
            df *= WEAKENED_DEF_MULT
        dr = df / (df + DEFENSE_DENOM)
        final_dmg = max(1, int(base_dmg * (1 - dr)))

    return base_dmg, final_dmg


def apply_damage_to_enemy(state: GameState, raw: float, skill: Optional[Skill]) -> Tuple[int, bool]:
    """Apply damage to enemy, accounting for defense and crits."""
    e = state.combat.enemy
    df = e.defense
    if skill and skill.type in ("magic", "magic_debuff", "mixed_magic"):
        df = e.m_def
    if skill and skill.armor_pierce:
        df *= (1 - skill.armor_pierce)
    if has_status(e, "weakened"):
        df *= WEAKENED_DEF_MULT
    dr = df / (df + DEFENSE_DENOM)
    dmg = max(1, int(raw * (1 - dr)))

    is_crit = False
    cc = state.crit
    if state.buffs.get("critUp", 0) > 0:
        cc += CRIT_UP_BONUS
    if state.buffs.get("atkCritUp", 0) > 0:
        cc += ATK_CRIT_UP_BONUS
    if skill and skill.flat_crit_bonus:
        cc += skill.flat_crit_bonus
    if skill and skill.guaranteed_crit:
        is_crit = True
    elif random.random() * 100 < cc:
        is_crit = True

    if is_crit:
        dmg = int(dmg * (CRIT_BASE_MULT + state.luck * 0.01))

    dmg = max(1, dmg)
    e.hp = max(0, e.hp - dmg)
    return dmg, is_crit


def _get_buff_defense_bonus(state: GameState, is_phys: bool) -> int:
    """Calculate DEF/mDEF percentage bonus from active buffs using registry."""
    pct = 0
    b = state.buffs
    for buff_key, phys_pct, magic_pct in DEFENSE_BUFF_TABLE:
        if b.get(buff_key, 0) > 0:
            pct += phys_pct if is_phys else magic_pct
    return pct


def _get_buff_evasion_bonus(state: GameState) -> int:
    """Calculate EVA bonus from active buffs using registry."""
    bonus = 0
    b = state.buffs
    for buff_key, eva_bonus in EVASION_BUFF_TABLE:
        if b.get(buff_key, 0) > 0:
            bonus += eva_bonus
    return bonus


def apply_damage_to_player(state: GameState, raw: float, is_phys: bool) -> Tuple[int, str]:
    """Apply damage to player with shield/barrier/evasion/buffs."""
    if state.barrier > 0 and raw > 0:
        state.barrier -= 1
        return 0, "barrier"

    if state.shield > 0 and raw > 0:
        if state.shield >= raw:
            state.shield -= raw
            return 0, "shield"
        else:
            raw -= state.shield
            state.shield = 0

    if state.buffs.get("divineInterv", 0) > 0:
        state.buffs["divineInterv"] -= 1
        return 0, "barrier"

    if state.buffs.get("ethereal", 0) > 0:
        return 0, "evade"

    if state.buffs.get("flicker", 0) > 0:
        if random.random() < 0.5:
            state.buffs["flicker"] -= 1
            return 0, "evade"

    eva = state.evasion + _get_buff_evasion_bonus(state)
    if random.random() * 100 < eva:
        return 0, "evade"

    # DEF/mDEF with buff bonuses (statSwap swaps which defense is used)
    if state.buffs.get("statSwap", 0) > 0:
        base_df = state.m_def if is_phys else state.defense
    else:
        base_df = state.defense if is_phys else state.m_def
    bonus_pct = _get_buff_defense_bonus(state, is_phys)
    df = base_df * (1 + bonus_pct / 100)
    dr = df / (df + DEFENSE_DENOM)
    dmg = max(1, int(raw * (1 - dr)))

    if state.buffs.get("mirrorImg", 0) > 0:
        dmg = int(dmg * MIRROR_IMG_REDUCTION)

    if state.buffs.get("undying", 0) > 0 and dmg >= state.hp:
        state.hp = 1
        return dmg, "undying"

    if state.buffs.get("undyingPact", 0) > 0 and dmg >= state.hp:
        state.hp = 1
        return dmg, "undying"

    if state.buffs.get("eldritchRebirth", 0) > 0 and dmg >= state.hp:
        state.hp = max(1, int(state.max_hp * ELDRITCH_REBIRTH_HP_PCT))
        del state.buffs["eldritchRebirth"]
        return dmg, "undying"

    if state.buffs.get("finalStand", 0) > 0:
        return 0, "barrier"

    state.hp = max(0, state.hp - dmg)
    state.hits_taken += 1

    if state.buffs.get("bloodAura", 0) > 0:
        heal = int(dmg * BLOOD_AURA_LS_PCT)
        state.hp = min(state.max_hp, state.hp + heal)

    if state.buffs.get("retribAura", 0) > 0 and state.combat:
        reflected = int(dmg * RETRIB_AURA_REFLECT_PCT)
        state.combat.enemy.hp = max(0, state.combat.enemy.hp - reflected)

    if state.buffs.get("dreadnought", 0) > 0:
        atk_bonus = int(dmg * DREADNOUGHT_CONVERSION_PCT)
        state.temp_stats["str"] = state.temp_stats.get("str", 0) + atk_bonus
        state.recalc_stats()

    return dmg, "hit"


def process_status_effects(target, is_player: bool, state: GameState) -> List[Tuple[str, str]]:
    """Process burning, poison, bleeding, etc. Returns list of log messages."""
    logs: List[Tuple[str, str]] = []
    to_remove: List[StatusEffect] = []
    for st in target.statuses:
        if st.type == "burning":
            d = int(target.max_hp * BURNING_HP_PCT) if hasattr(target, 'max_hp') else int(state.max_hp * BURNING_HP_PCT)
            target.hp = max(0, target.hp - d)
            who = "You burn" if is_player else f"{target.name} burns"
            logs.append((f"{who} for {d}!", "damage"))
        elif st.type == "poisoned":
            stacks = getattr(st, 'stacks', 1)
            d = int(target.max_hp * POISON_HP_PCT * stacks) if hasattr(target, 'max_hp') else int(state.max_hp * POISON_HP_PCT * stacks)
            target.hp = max(0, target.hp - d)
            who = "Poison" if is_player else f"Poison on {target.name}"
            logs.append((f"{who} deals {d}! ({stacks} stacks)", "damage"))
        elif st.type == "bleeding":
            d = int(target.max_hp * BLEEDING_HP_PCT) if hasattr(target, 'max_hp') else int(state.max_hp * BLEEDING_HP_PCT)
            target.hp = max(0, target.hp - d)
            who = "You bleed" if is_player else f"{target.name} bleeds"
            logs.append((f"{who} for {d}!", "damage"))

        st.duration -= 1
        if st.duration <= 0:
            to_remove.append(st)

    for st in to_remove:
        target.statuses.remove(st)
        if st.type == "doom" and not is_player:
            hp_pct = target.hp / target.max_hp if target.max_hp > 0 else 0
            if hp_pct < DOOM_HP_THRESHOLD:
                target.hp = 0
                logs.append((f"━━ THE YELLOW SIGN CLAIMS {target.name}! ━━", "crit"))
            else:
                logs.append((f"The Pallid Mask fades... {target.name} endures.", "info"))
        elif not is_player:
            logs.append((f"{st.type} wears off from {target.name}.", "info"))
        else:
            logs.append((f"{st.type} wears off.", "info"))
    return logs


def tick_player_buffs(state: GameState) -> List[Tuple[str, str]]:
    """Tick player buff durations and apply regen/oath effects."""
    logs: List[Tuple[str, str]] = []
    to_remove: List[str] = []
    for key in list(state.buffs.keys()):
        state.buffs[key] -= 1
        if key == "regen" and state.buffs[key] >= 0:
            h = int(state.max_hp * REGEN_HP_PCT)
            state.hp = min(state.max_hp, state.hp + h)
            logs.append((f"Regen heals {h} HP.", "heal"))
        elif key == "regen5" and state.buffs[key] >= 0:
            h = int(state.max_hp * REGEN5_HP_PCT)
            state.hp = min(state.max_hp, state.hp + h)
            logs.append((f"Regen heals {h} HP.", "heal"))
        elif key == "oath" and state.buffs[key] >= 0:
            h = int(state.max_hp * OATH_HP_PCT)
            state.hp = min(state.max_hp, state.hp + h)
            logs.append((f"Oath heals {h} HP.", "heal"))
        if state.buffs[key] <= 0:
            to_remove.append(key)

    STAT_BUFF_KEYS = {
        "permIntWis": ["int", "wis"],
        "permAtk2": ["str"],
        "permWisStr": ["wis", "str"],
        "permAgiLuk": ["agi", "luck"],
        "permAll1": ["int", "str", "agi", "wis", "luck"],
        "thickSkull": ["str", "wis"],
        "perseverance": ["wis", "str"],
        "shadowBless": ["agi", "luck"],
        "randStat2": ["int", "str", "agi", "wis", "luck"],
        "pallidMask": ["int", "str", "agi", "wis", "luck"],
        "dreadnought": ["str"],
    }

    for key in to_remove:
        del state.buffs[key]
        if key in STAT_BUFF_KEYS:
            for sk in STAT_BUFF_KEYS[key]:
                state.temp_stats.pop(sk, None)
            state.recalc_stats()
            logs.append((f"{key} — temporary stat boost expired.", "info"))
        elif key == "permCrit10":
            state.crit = max(0, state.crit - 25)
            logs.append(("Sixth Sense — CRIT bonus expired.", "info"))
        else:
            logs.append((f"{key} expired.", "info"))
    return logs


# ═══════════════════════════════════════════
# ENEMY AI
# ═══════════════════════════════════════════

def _get_enemy_intent_message(skill: Dict[str, Any]) -> str:
    """Generate a descriptive intent message for the enemy's next action."""
    stype = skill.get("type", "physical")
    sname = skill.get("name", "attack")

    if stype == "self_heal":
        return f"{sname} — the enemy channels restorative energy!"
    elif "debuff" in stype:
        return f"{sname} — the enemy prepares a dark technique!"
    elif stype == "magic":
        return f"{sname} — eldritch energy crackles in the air!"
    elif stype == "physical":
        return f"{sname} — the enemy braces for a strike!"
    else:
        return f"{sname} — the enemy readies itself!"


def enemy_turn(state: GameState) -> List[Tuple[str, str]]:
    """Execute enemy turn. Returns list of (text, type) log messages."""
    logs: List[Tuple[str, str]] = []
    c = state.combat
    e = c.enemy

    if e.stunned:
        e.stunned = False
        logs.append((f"{e.name} is stunned!", "effect"))
        return logs

    shocked = next((s for s in e.statuses if s.type == "shocked"), None)
    if shocked and random.random() < SHOCK_STUN_CHANCE:
        e.stunned = True
        logs.append((f"{e.name} stunned by shock!", "effect"))
        return logs

    if has_status(e, "blinded") and random.random() < BLIND_MISS_CHANCE:
        logs.append((f"{e.name} misses!", "info"))
        return logs

    if c.next_enemy_skill:
        skill = c.next_enemy_skill
        c.next_enemy_skill = None
    else:
        skill = random.choice(e.skills)
    stype = skill.get("type", "physical")
    spower = skill.get("power", 1.0)

    if stype in ("physical", "magic"):
        dmg = int(e.atk * spower * (ENEMY_VAR_LOW + random.random() * ENEMY_VAR_RANGE))
        if stype == "physical" and has_status(e, "freezing"):
            dmg = int(dmg * FREEZING_PHYS_MULT)
        if stype == "magic" and has_status(e, "petrified"):
            dmg = int(dmg * PETRIFIED_MAGIC_MULT)
        if has_status(e, "weakened"):
            dmg = int(dmg * WEAKENED_ATK_MULT)
        is_phys = stype == "physical"
        actual, result = apply_damage_to_player(state, dmg, is_phys)
        if actual > 0:
            logs.append((f"{e.name} uses {skill['name']} for {actual} damage!", "damage"))
        elif result == "evade":
            logs.append((f"You evade {e.name}'s attack!", "info"))
        elif result == "barrier":
            logs.append((f"Barrier absorbs {e.name}'s hit!", "shield"))
        elif result == "undying":
            logs.append(("Undying Fury keeps you alive!", "heal"))

    elif stype in ("physical_debuff", "magic_debuff"):
        dmg = int(e.atk * spower * (ENEMY_VAR_LOW + random.random() * ENEMY_VAR_RANGE))
        if "physical" in stype and has_status(e, "freezing"):
            dmg = int(dmg * FREEZING_PHYS_MULT)
        if "magic" in stype and has_status(e, "petrified"):
            dmg = int(dmg * PETRIFIED_MAGIC_MULT)
        if has_status(e, "weakened"):
            dmg = int(dmg * WEAKENED_ATK_MULT)
        is_phys = "physical" in stype
        actual, result = apply_damage_to_player(state, dmg, is_phys)

        if skill.get("effect"):
            apply_status_effect_on_player(state, skill["effect"], skill.get("duration", 2))

        if actual > 0:
            eff = skill.get("effect", "")
            logs.append((f"{e.name} uses {skill['name']} for {actual} + {eff}!", "damage"))
        elif result == "evade":
            logs.append((f"You evade {e.name}'s attack!", "info"))
        else:
            logs.append((f"{e.name} uses {skill['name']} — effect applied!", "effect"))

    elif stype == "self_heal":
        h = int(e.max_hp * spower)
        e.hp = min(e.max_hp, e.hp + h)
        logs.append((f"{e.name} heals {h} HP!", "heal"))

    return logs


# ═══════════════════════════════════════════
# STATUS EFFECT APPLICATION
# ═══════════════════════════════════════════

def apply_status_effect_on_player(state: GameState, effect_type: str, duration: int) -> None:
    """Apply a status effect to the player."""
    if effect_type:
        apply_status_player(state, effect_type, duration)


def apply_status_player(state: GameState, effect_type: str, duration: int) -> None:
    """Apply status to player's status list."""
    if state.buffs.get("immunity", 0) > 0:
        return
    existing = next((s for s in state.statuses if s.type == effect_type), None)
    if existing:
        existing.duration = max(existing.duration, duration)
    else:
        se = StatusEffect(effect_type, duration)
        state.statuses.append(se)
        if effect_type == "poisoned":
            se.stacks = 1
    if effect_type == "poisoned":
        existing = next((s for s in state.statuses if s.type == "poisoned"), None)
        if existing:
            existing.stacks = min(POISON_MAX_STACKS, existing.stacks + 1)


def process_player_status_effects(state: GameState) -> List[Tuple[str, str]]:
    """Process burning/poison/bleeding on the player."""
    logs: List[Tuple[str, str]] = []
    to_remove: List[StatusEffect] = []
    for st in state.statuses:
        if st.type == "burning":
            d = int(state.max_hp * BURNING_HP_PCT)
            state.hp = max(0, state.hp - d)
            logs.append((f"You burn for {d}!", "damage"))
        elif st.type == "poisoned":
            stacks = getattr(st, 'stacks', 1)
            d = int(state.max_hp * POISON_HP_PCT * stacks)
            state.hp = max(0, state.hp - d)
            logs.append((f"Poison deals {d}! ({stacks} stacks)", "damage"))
        elif st.type == "bleeding":
            d = int(state.max_hp * BLEEDING_HP_PCT)
            state.hp = max(0, state.hp - d)
            logs.append((f"You bleed for {d}!", "damage"))
        st.duration -= 1
        if st.duration <= 0:
            to_remove.append(st)
    for st in to_remove:
        state.statuses.remove(st)
        logs.append((f"{st.type} wears off.", "info"))
    return logs


# ═══════════════════════════════════════════
# BOSS PHASES & FLEE
# ═══════════════════════════════════════════

def check_boss_phase(state: GameState) -> List[Tuple[str, str]]:
    """Check and apply boss phase transitions."""
    c = state.combat
    if not c or not c.is_boss:
        return []
    e = c.enemy
    pct = e.hp / e.max_hp
    logs: List[Tuple[str, str]] = []

    if pct <= BOSS_PHASE3_HP and not c.phase3:
        c.phase3 = True
        e.atk = int(e.atk * BOSS_PHASE3_ATK_MULT)
        e.skills.append({"name": "Desperate Fury", "type": "physical", "power": 2.5})
        logs.append(("━━ HASTUR ENTERS FINAL PHASE! ATK increased! ━━", "crit"))

    elif pct <= BOSS_PHASE2_HP and not c.phase2:
        c.phase2 = True
        e.skills.append({"name": "Reality Tear", "type": "magic_debuff", "power": 2.0, "effect": "blinded", "duration": 2})
        e.skills.append({"name": "Maddening Whisper", "type": "magic_debuff", "power": 1.0, "effect": "shocked", "duration": 2})
        logs.append(("━━ THE KING UNRAVELS REALITY! New abilities! ━━", "crit"))

    return logs


def combat_run_attempt(state: GameState) -> bool:
    """Attempt to flee combat. Returns True if successful."""
    c = state.combat
    if not c:
        return False
    if c.is_boss:
        return False
    chance = FLEE_BASE_CHANCE + state.stats["agi"] * FLEE_AGI_MULTIPLIER
    if random.random() * 100 < chance:
        state.add_madness(FLEE_SUCCESS_MADNESS)
        return True
    else:
        state.add_madness(FLEE_FAIL_MADNESS)
        return False
