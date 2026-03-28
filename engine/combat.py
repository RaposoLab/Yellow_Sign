"""Combat system: damage calculation, status effects, enemy AI."""

import random
import math
from data import ENEMIES, BOSS
from engine.models import Item, StatusEffect, Enemy, CombatState, has_status, apply_status
from engine.items import generate_item
from engine.skills import player_use_skill


# ═══════════════════════════════════════════
# COMBAT SYSTEM
# ═══════════════════════════════════════════

def start_combat(state, is_boss=False):
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

def _base_damage(state, skill):
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

    if state.rage:
        bd *= 1.6
    if state.buffs.get("atkCritUp", 0) > 0:
        bd *= 1.4
    if state.buffs.get("warpTime", 0) > 0:
        bd *= 1.2
    if state.buffs.get("madPower", 0) > 0:
        bd *= 1.25
    if state.buffs.get("darkPact", 0) > 0:
        bd *= 1.3
    if state.buffs.get("shadowMeld", 0) > 0:
        bd *= 2.0
    if state.buffs.get("eclipse", 0) > 0:
        bd *= 1.3
    if state.buffs.get("ethereal", 0) > 0:
        bd *= 2.5

    if skill.multihit and skill.multihit > 1:
        bd *= skill.multihit

    if skill.execute_bonus and state.combat:
        e = state.combat.enemy
        if e and e.hp / e.max_hp < 0.25:
            bd *= 2.0

    if skill.luck_bonus:
        bd *= (1 + state.luck * 0.02)

    return bd


def calc_player_damage(state, skill):
    """Calculate raw player damage for a skill (with random variance)."""
    bd = _base_damage(state, skill)

    # Random variance
    bd *= (1 + random.random() * state.luck * 0.005)
    bd *= (0.85 + random.random() * 0.3)

    if skill.gamble:
        gm = 0.5 + random.random() * 2.5
        bd *= gm

    if skill.coin_flip:
        if random.random() < 0.5:
            bd = 0
            h = int(state.max_hp * 0.25)
            state.hp = min(state.max_hp, state.hp + h)
        else:
            bd *= 1.5

    return int(bd)


def calc_preview_damage(state, skill):
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
            df *= 0.8
        dr = df / (df + 50)
        final_dmg = max(1, int(base_dmg * (1 - dr)))

    return base_dmg, final_dmg

def apply_damage_to_enemy(state, raw, skill):
    """Apply damage to enemy, accounting for defense and crits."""
    e = state.combat.enemy
    df = e.defense
    if skill and skill.type in ("magic", "magic_debuff", "mixed_magic"):
        df = e.m_def
    if skill and skill.armor_pierce:
        df *= (1 - skill.armor_pierce)
    # Weakened debuff: enemy takes more damage (DEF reduced by 20%)
    if has_status(e, "weakened"):
        df *= 0.8
    dr = df / (df + 50)
    dmg = max(1, int(raw * (1 - dr)))

    is_crit = False
    cc = state.crit
    if state.buffs.get("critUp", 0) > 0:
        cc += 30
    if state.buffs.get("atkCritUp", 0) > 0:
        cc += 20
    if skill and skill.flat_crit_bonus:
        cc += skill.flat_crit_bonus
    if skill and skill.guaranteed_crit:
        is_crit = True
    elif random.random() * 100 < cc:
        is_crit = True

    if is_crit:
        dmg = int(dmg * (1.8 + state.luck * 0.01))

    dmg = max(1, dmg)
    e.hp = max(0, e.hp - dmg)
    return dmg, is_crit

def _get_buff_defense_bonus(state, is_phys):
    """Calculate DEF/mDEF percentage bonus from active buffs."""
    pct = 0
    b = state.buffs
    if is_phys:
        if b.get("thoughtform", 0) > 0:   pct += 30
        if b.get("ironSkin", 0) > 0:       pct += 60
        if b.get("chant", 0) > 0:          pct += 20
        if b.get("innerFire", 0) > 0:      pct += 15
        if b.get("hallowed", 0) > 0:       pct += 40
        if b.get("fortress", 0) > 0:       pct += 80
        if b.get("bulwark", 0) > 0:        pct += 60
        if b.get("umbralAegis", 0) > 0:    pct += 40
    else:
        if b.get("thoughtform", 0) > 0:   pct += 30
        if b.get("ironSkin", 0) > 0:       pct += 30
        if b.get("chant", 0) > 0:          pct += 20
        if b.get("innerFire", 0) > 0:      pct += 15
        if b.get("mDefUp", 0) > 0:         pct += 50
        if b.get("wardAura", 0) > 0:       pct += 30
        if b.get("hallowed", 0) > 0:       pct += 40
        if b.get("fortress", 0) > 0:       pct += 80
        if b.get("bulwark", 0) > 0:        pct += 60
        if b.get("dreamShell", 0) > 0:     pct += 80
        if b.get("astral", 0) > 0:         pct += 60
    return pct

def _get_buff_evasion_bonus(state):
    """Calculate EVA bonus from active buffs."""
    bonus = 0
    b = state.buffs
    if b.get("smokeScreen", 0) > 0:   bonus += 25
    if b.get("dreamVeil", 0) > 0:     bonus += 35
    if b.get("evasionUp", 0) > 0:     bonus += 40
    if b.get("dreamShell", 0) > 0:    bonus += 50
    if b.get("umbralAegis", 0) > 0:   bonus += 60
    if b.get("astral", 0) > 0:        bonus += 40
    return bonus

def apply_damage_to_player(state, raw, is_phys):
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

    # Divine Intervention: nullify next N attacks
    if state.buffs.get("divineInterv", 0) > 0:
        state.buffs["divineInterv"] -= 1
        return 0, "barrier"

    # Ethereal: invulnerable this turn
    if state.buffs.get("ethereal", 0) > 0:
        return 0, "evade"

    # Flicker: 50% dodge per stack
    if state.buffs.get("flicker", 0) > 0:
        if random.random() < 0.5:
            state.buffs["flicker"] -= 1
            return 0, "evade"

    # Evasion with buff bonuses
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
    dr = df / (df + 50)
    dmg = max(1, int(raw * (1 - dr)))

    # Mirror Images: 30% damage reduction
    if state.buffs.get("mirrorImg", 0) > 0:
        dmg = int(dmg * 0.7)

    if state.buffs.get("undying", 0) > 0 and dmg >= state.hp:
        state.hp = 1
        return dmg, "undying"

    # Undying Pact: can't die while active
    if state.buffs.get("undyingPact", 0) > 0 and dmg >= state.hp:
        state.hp = 1
        return dmg, "undying"

    # Eldritch Rebirth: auto-revive at 30% HP once
    if state.buffs.get("eldritchRebirth", 0) > 0 and dmg >= state.hp:
        state.hp = max(1, int(state.max_hp * 0.30))
        del state.buffs["eldritchRebirth"]
        return dmg, "undying"

    # Final Stand: invulnerable
    if state.buffs.get("finalStand", 0) > 0:
        return 0, "barrier"

    state.hp = max(0, state.hp - dmg)
    state.hits_taken += 1

    # Blood Aura: lifesteal 10% on damage taken (counter-intuitive but works as passive drain)
    if state.buffs.get("bloodAura", 0) > 0:
        heal = int(dmg * 0.10)
        state.hp = min(state.max_hp, state.hp + heal)

    # Retribution Aura: reflect 30% damage back to enemy
    if state.buffs.get("retribAura", 0) > 0 and state.combat:
        reflected = int(dmg * 0.30)
        state.combat.enemy.hp = max(0, state.combat.enemy.hp - reflected)

    # Dreadnought: convert damage taken into ATK bonus
    if state.buffs.get("dreadnought", 0) > 0:
        atk_bonus = int(dmg * 0.5)
        state.temp_stats["str"] = state.temp_stats.get("str", 0) + atk_bonus
        state.recalc_stats()

    return dmg, "hit"

def process_status_effects(target, is_player, state):
    """Process burning, poison, bleeding, etc. Returns list of log messages."""
    logs = []
    to_remove = []
    for st in target.statuses:
        if st.type == "burning":
            d = int(target.max_hp * 0.06) if hasattr(target, 'max_hp') else int(state.max_hp * 0.06)
            target.hp = max(0, target.hp - d)
            who = "You burn" if is_player else f"{target.name} burns"
            logs.append((f"{who} for {d}!", "damage"))
        elif st.type == "poisoned":
            stacks = getattr(st, 'stacks', 1)
            d = int(target.max_hp * 0.04 * stacks) if hasattr(target, 'max_hp') else int(state.max_hp * 0.04 * stacks)
            target.hp = max(0, target.hp - d)
            who = "Poison" if is_player else f"Poison on {target.name}"
            logs.append((f"{who} deals {d}! ({stacks} stacks)", "damage"))
        elif st.type == "bleeding":
            d = int(target.max_hp * 0.05) if hasattr(target, 'max_hp') else int(state.max_hp * 0.05)
            target.hp = max(0, target.hp - d)
            who = "You bleed" if is_player else f"{target.name} bleeds"
            logs.append((f"{who} for {d}!", "damage"))

        st.duration -= 1
        if st.duration <= 0:
            to_remove.append(st)

    for st in to_remove:
        target.statuses.remove(st)
        if st.type == "doom" and not is_player:
            # Doom triggers: instant kill if below 30% HP
            hp_pct = target.hp / target.max_hp if target.max_hp > 0 else 0
            if hp_pct < 0.30:
                target.hp = 0
                logs.append((f"━━ THE YELLOW SIGN CLAIMS {target.name}! ━━", "crit"))
            else:
                logs.append((f"The Pallid Mask fades... {target.name} endures.", "info"))
        elif not is_player:
            logs.append((f"{st.type} wears off from {target.name}.", "info"))
        else:
            logs.append((f"{st.type} wears off.", "info"))
    return logs

def tick_player_buffs(state):
    """Tick player buff durations and apply regen/oath effects."""
    logs = []
    to_remove = []
    for key in list(state.buffs.keys()):
        state.buffs[key] -= 1
        if key == "regen" and state.buffs[key] >= 0:
            h = int(state.max_hp * 0.08)
            state.hp = min(state.max_hp, state.hp + h)
            logs.append((f"Regen heals {h} HP.", "heal"))
        elif key == "regen5" and state.buffs[key] >= 0:
            h = int(state.max_hp * 0.05)
            state.hp = min(state.max_hp, state.hp + h)
            logs.append((f"Regen heals {h} HP.", "heal"))
        elif key == "oath" and state.buffs[key] >= 0:
            h = int(state.max_hp * 0.10)
            state.hp = min(state.max_hp, state.hp + h)
            logs.append((f"Oath heals {h} HP.", "heal"))
        if state.buffs[key] <= 0:
            to_remove.append(key)

    # Mapping of stat buff types to their temp_stats keys
    STAT_BUFF_KEYS = {
        "permIntWis": ["int", "wis"],
        "permAtk2": ["str"],
        "permWisStr": ["wis", "str"],
        "permAgiLuk": ["agi", "luck"],
        "permAll1": ["int", "str", "agi", "wis", "luck"],
        "thickSkull": ["str", "wis"],
        "perseverance": ["wis", "str"],
        "shadowBless": ["agi", "luck"],
        "randStat2": ["int", "str", "agi", "wis", "luck"],  # cleared fully on expire
        "pallidMask": ["int", "str", "agi", "wis", "luck"],
        "dreadnought": ["str"],
    }

    for key in to_remove:
        del state.buffs[key]
        # Clean up temp stats if this was a stat buff
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
# SKILL HANDLERS (extracted from player_use_skill)
# ═══════════════════════════════════════════

# Maps heal_calc names → (calc_fn, message_template, extra_fn)
# calc_fn(state, skill) → heal_amount (int)
# extra_fn(state, skill) is called after heal (optional side effects)

# Heal handler registry: heal_calc name → (calc_fn, message)

# Shield handler registry: shield_calc name → (build_fn, message)
# build_fn(state, skill) → shield_value (int), or None if custom logic

# Buff handler registry: buff_type → (apply_fn, message)
# apply_fn(state, skill) → None (mutates state directly)

# Static messages per buff_type (most don't need dynamic formatting)

# ═══════════════════════════════════════════
# MAIN SKILL DISPATCHER
# ═══════════════════════════════════════════

def _get_enemy_intent_message(skill):
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

def enemy_turn(state):
    """Execute enemy turn. Returns list of (text, type) log messages."""
    logs = []
    c = state.combat
    e = c.enemy

    if e.stunned:
        e.stunned = False
        logs.append((f"{e.name} is stunned!", "effect"))
        return logs

    # Shock stun check
    shocked = next((s for s in e.statuses if s.type == "shocked"), None)
    if shocked and random.random() < 0.5:
        e.stunned = True
        logs.append((f"{e.name} stunned by shock!", "effect"))
        return logs

    # Blind miss check
    if has_status(e, "blinded") and random.random() < 0.5:
        logs.append((f"{e.name} misses!", "info"))
        return logs

    # Use pre-selected skill if available, otherwise pick randomly
    if c.next_enemy_skill:
        skill = c.next_enemy_skill
        c.next_enemy_skill = None
    else:
        skill = random.choice(e.skills)
    stype = skill.get("type", "physical")
    spower = skill.get("power", 1.0)

    if stype in ("physical", "magic"):
        dmg = int(e.atk * spower * (0.85 + random.random() * 0.3))
        if stype == "physical" and has_status(e, "freezing"):
            dmg = int(dmg * 0.75)
        if stype == "magic" and has_status(e, "petrified"):
            dmg = int(dmg * 0.75)
        if has_status(e, "weakened"):
            dmg = int(dmg * 0.8)
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
        dmg = int(e.atk * spower * (0.85 + random.random() * 0.3))
        if "physical" in stype and has_status(e, "freezing"):
            dmg = int(dmg * 0.75)
        if "magic" in stype and has_status(e, "petrified"):
            dmg = int(dmg * 0.75)
        if has_status(e, "weakened"):
            dmg = int(dmg * 0.8)
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

def apply_status_effect_on_player(state, effect_type, duration):
    """Apply a status effect to the player."""
    if effect_type:
        apply_status_player(state, effect_type, duration)

def apply_status_player(state, effect_type, duration):
    """Apply status to player's status list."""
    # Debuff immunity check
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
    # Stack poison
    if effect_type == "poisoned":
        existing = next((s for s in state.statuses if s.type == "poisoned"), None)
        if existing:
            existing.stacks = min(5, existing.stacks + 1)

def process_player_status_effects(state):
    """Process burning/poison/bleeding on the player."""
    logs = []
    to_remove = []
    for st in state.statuses:
        if st.type == "burning":
            d = int(state.max_hp * 0.06)
            state.hp = max(0, state.hp - d)
            logs.append((f"You burn for {d}!", "damage"))
        elif st.type == "poisoned":
            stacks = getattr(st, 'stacks', 1)
            d = int(state.max_hp * 0.04 * stacks)
            state.hp = max(0, state.hp - d)
            logs.append((f"Poison deals {d}! ({stacks} stacks)", "damage"))
        elif st.type == "bleeding":
            d = int(state.max_hp * 0.05)
            state.hp = max(0, state.hp - d)
            logs.append((f"You bleed for {d}!", "damage"))
        st.duration -= 1
        if st.duration <= 0:
            to_remove.append(st)
    for st in to_remove:
        state.statuses.remove(st)
        logs.append((f"{st.type} wears off.", "info"))
    return logs

def check_boss_phase(state):
    """Check and apply boss phase transitions."""
    c = state.combat
    if not c or not c.is_boss:
        return []
    e = c.enemy
    pct = e.hp / e.max_hp
    logs = []

    if pct <= 0.25 and not c.phase3:
        c.phase3 = True
        e.atk = int(e.atk * 1.4)
        e.skills.append({"name": "Desperate Fury", "type": "physical", "power": 2.5})
        logs.append(("━━ HASTUR ENTERS FINAL PHASE! ATK increased! ━━", "crit"))

    elif pct <= 0.5 and not c.phase2:
        c.phase2 = True
        e.skills.append({"name": "Reality Tear", "type": "magic_debuff", "power": 2.0, "effect": "blinded", "duration": 2})
        e.skills.append({"name": "Maddening Whisper", "type": "magic_debuff", "power": 1.0, "effect": "shocked", "duration": 2})
        logs.append(("━━ THE KING UNRAVELS REALITY! New abilities! ━━", "crit"))

    return logs

def combat_run_attempt(state):
    """Attempt to flee combat. Returns True if successful."""
    c = state.combat
    if not c:
        return False
    if c.is_boss:
        return False  # Can't flee from boss
    chance = 40 + state.stats["agi"] * 2
    if random.random() * 100 < chance:
        state.add_madness(5)
        return True
    else:
        state.add_madness(3)
        return False
