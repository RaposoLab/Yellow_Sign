"""
Buff/Debuff Registry — central definitions for all status effects.
Each entry: symbol, 2-letter uppercase abbreviation, display name, description, category, color.

Color convention:
  - Debuffs: negative colors (dark red, purple, black, sickly green)
  - Buffs: positive colors (gold, blue, white, bright green)
"""

EFFECT_REGISTRY = {
    # ═══════════════════════════════════════
    # DEBUFFS — negative colors
    # ═══════════════════════════════════════
    "burning": {
        "letter": "BU",
        "name": "Burning",
        "desc": "Losing 6% max HP per turn as fire damage.",
        "category": "debuff",
        "color": (200, 50, 30),
    },
    "poisoned": {
        "letter": "PO",
        "name": "Poisoned",
        "desc": "Losing 4% max HP per turn per stack (max 5 stacks).",
        "category": "debuff",
        "color": (60, 160, 40),
    },
    "bleeding": {
        "letter": "BL",
        "name": "Bleeding",
        "desc": "Losing 5% max HP per turn from open wounds.",
        "category": "debuff",
        "color": (180, 20, 20),
    },
    "shocked": {
        "letter": "SH",
        "name": "Shocked",
        "desc": "50% chance to be stunned each turn, losing your action.",
        "category": "debuff",
        "color": (120, 80, 200),
    },
    "blinded": {
        "letter": "BN",
        "name": "Blinded",
        "desc": "50% chance to miss attacks.",
        "category": "debuff",
        "color": (100, 80, 120),
    },
    "freezing": {
        "letter": "FR",
        "name": "Freezing",
        "desc": "Physical attack damage reduced by 25%.",
        "category": "debuff",
        "color": (80, 60, 160),
    },
    "petrified": {
        "letter": "PT",
        "name": "Petrified",
        "desc": "Magic attack damage reduced by 25%.",
        "category": "debuff",
        "color": (100, 80, 60),
    },
    "weakened": {
        "letter": "WK",
        "name": "Weakened",
        "desc": "Attack damage reduced by 20%. Defense reduced by 20%.",
        "category": "debuff",
        "color": (160, 80, 40),
    },
    "doom": {
        "letter": "DM",
        "name": "Doom",
        "desc": "When this expires: instant death if below 30% HP. The Yellow Sign claims its due.",
        "category": "debuff",
        "color": (180, 40, 40),
    },
    "stunned": {
        "letter": "ST",
        "name": "Stunned",
        "desc": "Cannot act this turn.",
        "category": "debuff",
        "color": (180, 140, 40),
    },

    # ═══════════════════════════════════════
    # BUFFS — positive colors
    # ═══════════════════════════════════════

    # Regen / healing over time
    "regen": {
        "letter": "RG",
        "name": "Regeneration",
        "desc": "Healing 8% max HP each turn.",
        "category": "buff",
        "color": (80, 220, 120),
    },
    "regen5": {
        "letter": "RG",
        "name": "Regeneration",
        "desc": "Healing 5% max HP each turn.",
        "category": "buff",
        "color": (80, 220, 120),
    },
    "oath": {
        "letter": "OA",
        "name": "Oath of Renewal",
        "desc": "Healing 10% max HP each turn.",
        "category": "buff",
        "color": (100, 240, 160),
    },

    # Defensive buffs
    "thoughtform": {
        "letter": "TF",
        "name": "Thoughtform Barrier",
        "desc": "+30% physical and magic defense.",
        "category": "buff",
        "color": (160, 180, 240),
    },
    "ironSkin": {
        "letter": "IS",
        "name": "Iron Skin",
        "desc": "+60% physical defense, +30% magic defense.",
        "category": "buff",
        "color": (200, 200, 220),
    },
    "chant": {
        "letter": "CH",
        "name": "Chant of Warding",
        "desc": "+20% physical and magic defense.",
        "category": "buff",
        "color": (180, 160, 240),
    },
    "innerFire": {
        "letter": "IF",
        "name": "Inner Fire",
        "desc": "+15% physical and magic defense.",
        "category": "buff",
        "color": (240, 180, 80),
    },
    "mDefUp": {
        "letter": "MD",
        "name": "Magic Ward",
        "desc": "+50% magic defense.",
        "category": "buff",
        "color": (120, 160, 240),
    },
    "wardAura": {
        "letter": "WA",
        "name": "Ward Aura",
        "desc": "+30% magic defense.",
        "category": "buff",
        "color": (140, 180, 255),
    },
    "hallowed": {
        "letter": "HA",
        "name": "Hallowed Ground",
        "desc": "+40% physical and magic defense.",
        "category": "buff",
        "color": (240, 220, 120),
    },
    "fortress": {
        "letter": "FO",
        "name": "Fortress",
        "desc": "+80% physical and magic defense. Massive fortification.",
        "category": "buff",
        "color": (180, 180, 200),
    },
    "bulwark": {
        "letter": "BW",
        "name": "Bulwark",
        "desc": "+60% physical and magic defense.",
        "category": "buff",
        "color": (160, 160, 190),
    },
    "umbralAegis": {
        "letter": "UA",
        "name": "Umbral Aegis",
        "desc": "+40% physical DEF, +60% magic DEF, +25 EVA.",
        "category": "buff",
        "color": (140, 120, 200),
    },
    "dreamShell": {
        "letter": "DS",
        "name": "Dream Shell",
        "desc": "+80% magic defense, +25 evasion.",
        "category": "buff",
        "color": (180, 160, 240),
    },
    "astral": {
        "letter": "AS",
        "name": "Astral Projection",
        "desc": "+40 evasion, +60% magic defense.",
        "category": "buff",
        "color": (200, 180, 255),
    },

    # Evasion buffs
    "smokeScreen": {
        "letter": "SS",
        "name": "Smoke Screen",
        "desc": "+25 evasion chance.",
        "category": "buff",
        "color": (160, 180, 200),
    },
    "dreamVeil": {
        "letter": "DV",
        "name": "Dream Veil",
        "desc": "+35 evasion chance.",
        "category": "buff",
        "color": (180, 160, 240),
    },
    "evasionUp": {
        "letter": "EV",
        "name": "Evasion Up",
        "desc": "+40 evasion chance.",
        "category": "buff",
        "color": (120, 220, 140),
    },

    # Special defensive
    "divineInterv": {
        "letter": "DI",
        "name": "Divine Intervention",
        "desc": "Nullifies the next N attacks completely.",
        "category": "buff",
        "color": (255, 240, 120),
    },
    "ethereal": {
        "letter": "ET",
        "name": "Ethereal",
        "desc": "Invulnerable this turn. Next attack deals +150% damage (then consumed).",
        "category": "buff",
        "color": (200, 200, 255),
    },
    "flicker": {
        "letter": "FL",
        "name": "Flicker",
        "desc": "50% dodge chance per stack. Decrements on proc.",
        "category": "buff",
        "color": (220, 200, 255),
    },
    "mirrorImg": {
        "letter": "MI",
        "name": "Mirror Images",
        "desc": "30% damage reduction from incoming attacks.",
        "category": "buff",
        "color": (180, 180, 240),
    },
    "undying": {
        "letter": "UN",
        "name": "Undying Fury",
        "desc": "Cannot die while active. HP is set to 1 instead of 0.",
        "category": "buff",
        "color": (240, 100, 100),
    },
    "undyingPact": {
        "letter": "UP",
        "name": "Undying Pact",
        "desc": "Cannot die while active. HP is set to 1 instead of 0.",
        "category": "buff",
        "color": (240, 100, 120),
    },
    "eldritchRebirth": {
        "letter": "ER",
        "name": "Eldritch Rebirth",
        "desc": "Auto-revive at 30% HP if killed. Consumed on proc.",
        "category": "buff",
        "color": (140, 220, 160),
    },
    "finalStand": {
        "letter": "FS",
        "name": "Final Stand",
        "desc": "Invulnerable. Nothing can harm you.",
        "category": "buff",
        "color": (240, 220, 80),
    },
    "bloodAura": {
        "letter": "BA",
        "name": "Blood Aura",
        "desc": "10% lifesteal on damage taken.",
        "category": "buff",
        "color": (220, 80, 80),
    },
    "retribAura": {
        "letter": "RA",
        "name": "Retribution Aura",
        "desc": "Reflects 30% of damage taken back to the attacker.",
        "category": "buff",
        "color": (240, 160, 80),
    },
    "statSwap": {
        "letter": "SW",
        "name": "Mind Over Matter",
        "desc": "Physical and magic defense are swapped.",
        "category": "buff",
        "color": (180, 140, 220),
    },
    "dreadnought": {
        "letter": "DR",
        "name": "Dreadnought",
        "desc": "50% of damage taken is converted into temporary STR bonus.",
        "category": "buff",
        "color": (220, 100, 100),
    },

    # Damage buffs
    "rage": {
        "letter": "RA",
        "name": "Berserker Rage",
        "desc": "+60% damage dealt.",
        "category": "buff",
        "color": (240, 80, 60),
    },
    "atkCritUp": {
        "letter": "AC",
        "name": "Battle Fury",
        "desc": "+40% damage, +20% crit chance.",
        "category": "buff",
        "color": (240, 140, 60),
    },
    "warpTime": {
        "letter": "WT",
        "name": "Warp Time",
        "desc": "+20% damage dealt.",
        "category": "buff",
        "color": (180, 140, 240),
    },
    "madPower": {
        "letter": "MP",
        "name": "Mad Power",
        "desc": "+25% damage dealt through madness-fueled strength.",
        "category": "buff",
        "color": (200, 120, 220),
    },
    "darkPact": {
        "letter": "DP",
        "name": "Dark Pact",
        "desc": "+30% damage dealt at a terrible cost.",
        "category": "buff",
        "color": (180, 80, 200),
    },
    "shadowMeld": {
        "letter": "SM",
        "name": "Shadow Meld",
        "desc": "+100% damage dealt from the shadows.",
        "category": "buff",
        "color": (120, 100, 200),
    },
    "eclipse": {
        "letter": "EC",
        "name": "Eclipse",
        "desc": "+30% damage dealt under the darkened sky.",
        "category": "buff",
        "color": (140, 120, 200),
    },

    # Utility
    "madImmune": {
        "letter": "MI",
        "name": "Madness Immunity",
        "desc": "Madness can no longer cause death.",
        "category": "buff",
        "color": (140, 240, 200),
    },
    "immunity": {
        "letter": "IM",
        "name": "Debuff Immunity",
        "desc": "Immune to all debuffs.",
        "category": "buff",
        "color": (240, 240, 140),
    },
    "calmMind": {
        "letter": "CM",
        "name": "Calm Mind",
        "desc": "Madness reduced by 3.",
        "category": "buff",
        "color": (120, 200, 220),
    },

    # Stat buffs (temporary)
    "permIntWis": {
        "letter": "IW",
        "name": "Forbidden Knowledge",
        "desc": "INT +6, WIS +4 for 5 turns.",
        "category": "buff",
        "color": (180, 160, 240),
    },
    "permAtk2": {
        "letter": "WP",
        "name": "Warpaint",
        "desc": "STR +5 for 5 turns.",
        "category": "buff",
        "color": (240, 120, 100),
    },
    "permWisStr": {
        "letter": "OW",
        "name": "Oath of the Warden",
        "desc": "WIS +6, STR +4 for 5 turns.",
        "category": "buff",
        "color": (140, 200, 240),
    },
    "permAgiLuk": {
        "letter": "PA",
        "name": "Perfect Assassin",
        "desc": "AGI +7, LUCK +4 for 5 turns.",
        "category": "buff",
        "color": (120, 240, 140),
    },
    "permCrit10": {
        "letter": "CR",
        "name": "Sixth Sense",
        "desc": "+25% critical hit chance for 4 turns.",
        "category": "buff",
        "color": (255, 220, 80),
    },
    "permAll1": {
        "letter": "VA",
        "name": "Vision of the End",
        "desc": "All stats +4 for 5 turns.",
        "category": "buff",
        "color": (200, 180, 255),
    },
    "thickSkull": {
        "letter": "TS",
        "name": "Thick Skull",
        "desc": "STR +4, WIS +3 for 5 turns.",
        "category": "buff",
        "color": (200, 180, 160),
    },
    "perseverance": {
        "letter": "PR",
        "name": "Perseverance",
        "desc": "WIS +4, STR +3 for 5 turns.",
        "category": "buff",
        "color": (140, 200, 240),
    },
    "shadowBless": {
        "letter": "SB",
        "name": "Shadow's Blessing",
        "desc": "AGI +4, LUCK +3 for 5 turns.",
        "category": "buff",
        "color": (120, 120, 200),
    },
    "randStat2": {
        "letter": "PI",
        "name": "Prophetic Insight",
        "desc": "2 random stats +3 for 5 turns.",
        "category": "buff",
        "color": (180, 160, 240),
    },
    "pallidMask": {
        "letter": "PM",
        "name": "The Pallid Mask",
        "desc": "+50% all stats, immune to debuffs for 3 turns.",
        "category": "buff",
        "color": (220, 220, 180),
    },

    # Barrier
    "barrier": {
        "letter": "BR",
        "name": "Barrier",
        "desc": "Absorbs the next N hits completely.",
        "category": "buff",
        "color": (120, 200, 255),
    },

    # Misc buffs
    "abyssFort": {
        "letter": "AF",
        "name": "Abyssal Fortitude",
        "desc": "+50% physical defense, +1 barrier stack.",
        "category": "buff",
        "color": (160, 140, 220),
    },
    "warlord": {
        "letter": "WL",
        "name": "Warlord's Command",
        "desc": "Rage + Battle Fury + Iron Skin active. -20% HP cost.",
        "category": "buff",
        "color": (240, 100, 60),
    },
    "bloodRitual": {
        "letter": "BR",
        "name": "Blood Ritual",
        "desc": "Sacrificed 15% HP to gain 50 XP.",
        "category": "special",
        "color": (200, 60, 60),
    },
    "resetCds": {
        "letter": "RC",
        "name": "Cooldown Reset",
        "desc": "All ability cooldowns have been reset.",
        "category": "buff",
        "color": (120, 220, 220),
    },
    "eldritchBargain": {
        "letter": "EB",
        "name": "Eldritch Bargain",
        "desc": "Traded 3 points in 3 random stats for 50 gold.",
        "category": "special",
        "color": (200, 160, 80),
    },
    "prophetRes": {
        "letter": "RE",
        "name": "Prophet's Resilience",
        "desc": "Regen 6% HP/turn. +5 MAD.",
        "category": "buff",
        "color": (140, 200, 160),
    },
    "realityAnchor": {
        "letter": "RA",
        "name": "Reality Anchor",
        "desc": "Cannot die for 2 turns.",
        "category": "buff",
        "color": (160, 200, 240),
    },
    "foolLuck": {
        "letter": "FL",
        "name": "The Fool's Luck",
        "desc": "-10 MAD. Nullifies the next 3 attacks.",
        "category": "buff",
        "color": (240, 220, 80),
    },
    "nimbleFingers": {
        "letter": "NF",
        "name": "Nimble Fingers",
        "desc": "+20% improved loot quality. Higher chance of rare and cursed items.",
        "category": "buff",
        "color": (220, 200, 80),
    },
    "looterInst": {
        "letter": "LI",
        "name": "Looter's Instinct",
        "desc": "+10% improved loot quality. Higher chance of rare and cursed items.",
        "category": "buff",
        "color": (200, 180, 60),
    },
}


def get_effect_info(effect_type):
    """Get the registry entry for an effect type. Returns defaults if not found."""
    info = EFFECT_REGISTRY.get(effect_type)
    if info:
        return info
    # Fallback for unknown effects
    return {
        "letter": effect_type[:2].upper() if effect_type else "??",
        "name": effect_type.replace("_", " ").title() if effect_type else "Unknown",
        "desc": "An unknown effect.",
        "category": "buff",
        "color": (150, 150, 150),
    }
