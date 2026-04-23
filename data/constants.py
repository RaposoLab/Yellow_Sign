"""Game constants: sprite/icon mappings, combat formulas, status effects, UI."""

MAX_ACTIVE_SKILLS = 4

# ═══════════════════════════════════════════
# COMBAT FORMULA CONSTANTS
# ═══════════════════════════════════════════

# Defense formula: damage_reduction = defense / (defense + DEFENSE_DENOM)
DEFENSE_DENOM = 50

# Crit multiplier base (modified by luck: crit_mult = CRIT_BASE_MULT + luck * 0.01)
CRIT_BASE_MULT = 1.8

# Random variance range for damage: base * (DMG_VARIANCE_LOW + random() * DMG_VARIANCE_RANGE)
DMG_VARIANCE_LOW = 0.85
DMG_VARIANCE_RANGE = 0.3

# Luck damage variance: multiplied by 1 + luck * LUCK_DMG_VARIANCE
LUCK_DMG_VARIANCE = 0.005

# Luck bonus damage: multiplied by 1 + luck * LUCK_BONUS_DAMAGE_MULT
LUCK_BONUS_DAMAGE_MULT = 0.02

# Coin flip heads chance
COIN_FLIP_HEADS_CHANCE = 0.5

# Flicker dodge chance
FLICKER_DODGE_CHANCE = 0.5

# Blade Aura proc chance
BLADE_AURA_PROC_CHANCE = 0.15

# Low HP scaling max multiplier: 1 + (1 - hp_ratio) * LOW_HP_SCALING_MAX
LOW_HP_SCALING_MAX = 2.0

# Madness scaling max: 1 + madness / MADNESS_SCALING_MAX
MADNESS_SCALING_MAX = 100

# Enemy damage variance: atk * power * (ENEMY_VAR_LOW + random() * ENEMY_VAR_RANGE)
ENEMY_VAR_LOW = 0.85
ENEMY_VAR_RANGE = 0.3

# Flee base chance + agi * FLEE_AGI_MULTIPLIER
FLEE_BASE_CHANCE = 40
FLEE_AGI_MULTIPLIER = 2
FLEE_SUCCESS_MADNESS = 5
FLEE_FAIL_MADNESS = 3

# Execute threshold: bonus damage when enemy HP ratio < this
EXECUTE_HP_THRESHOLD = 0.25
EXECUTE_DAMAGE_MULT = 2.0

# Coin flip heal on tails: heals this fraction of max HP
COIN_FLIP_HEAL_FRAC = 0.25
COIN_FLIP_DAMAGE_MULT = 1.5

# Gambler damage range: multiplier = GAMBLE_MIN + random() * GAMBLE_RANGE
GAMBLE_MIN = 0.5
GAMBLE_RANGE = 2.5

# Doom kill threshold: instant kill if HP ratio < this when doom expires
DOOM_HP_THRESHOLD = 0.30

# Boss phase thresholds
BOSS_PHASE2_HP = 0.50
BOSS_PHASE3_HP = 0.25
BOSS_PHASE3_ATK_MULT = 1.4

# ═══════════════════════════════════════════
# STATUS EFFECT DOT PERCENTAGES (of max HP)
# ═══════════════════════════════════════════

BURNING_HP_PCT = 0.06
POISON_HP_PCT = 0.04
BLEEDING_HP_PCT = 0.05
POISON_MAX_STACKS = 5

# Debuff severity multipliers on enemy damage
FREEZING_PHYS_MULT = 0.75
PETRIFIED_MAGIC_MULT = 0.75
WEAKENED_ATK_MULT = 0.80
WEAKENED_DEF_MULT = 0.80

# Shock stun chance
SHOCK_STUN_CHANCE = 0.5

# Blind miss chance (enemy)
BLIND_MISS_CHANCE = 0.5

# ═══════════════════════════════════════════
# REGEN / HEAL-OVER-TIME PERCENTAGES
# ═══════════════════════════════════════════

REGEN_HP_PCT = 0.08
REGEN5_HP_PCT = 0.05
OATH_HP_PCT = 0.10
ADVANCE_FLOOR_HEAL_PCT = 0.10

# ═══════════════════════════════════════════
# DAMAGE BUFF MULTIPLIERS
# ═══════════════════════════════════════════

# Registry: buff_type → damage multiplier applied in _base_damage()
DAMAGE_BUFF_MULTIPLIERS = {
    "rage": 1.6,
    "atkCritUp": 1.4,
    "warpTime": 1.2,
    "madPower": 1.25,
    "darkPact": 1.3,
    "shadowMeld": 2.0,
    "eclipse": 1.3,
    "ethereal": 2.5,
    "undyingPact": 1.5,
}

# ═══════════════════════════════════════════
# DEFENSE BUFF REGISTRY
# ═══════════════════════════════════════════

# (buff_type, phys_pct, magic_pct) — applied in _get_buff_defense_bonus()
DEFENSE_BUFF_TABLE = [
    ("thoughtform", 30, 30),
    ("ironSkin", 60, 30),
    ("chant", 20, 20),
    ("innerFire", 15, 15),
    ("hallowed", 40, 40),
    ("fortress", 80, 80),
    ("bulwark", 60, 60),
    ("umbralAegis", 40, 0),
    ("mDefUp", 0, 50),
    ("wardAura", 0, 30),
    ("dreamShell", 0, 80),
    ("astral", 0, 60),
]

# (buff_type, evasion_bonus)
EVASION_BUFF_TABLE = [
    ("smokeScreen", 25),
    ("dreamVeil", 35),
    ("evasionUp", 40),
    ("dreamShell", 50),
    ("umbralAegis", 60),
    ("astral", 40),
    ("darkRegenBuff", 20),
    ("fadeBlack", 20),
    ("critUp", 15),
    ("luckyDodge", 35),
]

# ═══════════════════════════════════════════
# DEFENSE ON-TAKE-DAMAGE BUFFS
# ═══════════════════════════════════════════

# Mirror Images damage reduction multiplier
MIRROR_IMG_REDUCTION = 0.7

# Blood Aura lifesteal on damage taken
BLOOD_AURA_LS_PCT = 0.10

# Retribution Aura reflect percentage
RETRIB_AURA_REFLECT_PCT = 0.30

# Dreadnought: damage taken → STR bonus conversion
DREADNOUGHT_CONVERSION_PCT = 0.50

# Eldritch Rebirth: revive at this HP fraction
ELDRITCH_REBIRTH_HP_PCT = 0.30

# ═══════════════════════════════════════════
# CRIT BUFF BONUSES
# ═══════════════════════════════════════════

CRIT_UP_BONUS = 30
ATK_CRIT_UP_BONUS = 20

# ═══════════════════════════════════════════
# STAT / LEVEL-UP CONSTANTS
# ═══════════════════════════════════════════

XP_GROWTH_RATE = 1.3
LEVEL_UP_HP_BONUS = 15

# XP/Gold rewards per combat
XP_BASE = 12
XP_PER_FLOOR = 4
XP_BOSS_BONUS = 80
GOLD_BASE = 6
GOLD_PER_FLOOR = 2
GOLD_BOSS_BONUS = 50
GOLD_BASE_RANDOM_MAX = 8

# Madness changes
MADNESS_BOSS_KILL = -15
MADNESS_NORMAL_KILL = 3
MADNESS_MAX = 100

# Max barrier stacks
MAX_BARRIER_STACKS = 3

# Stat keys used throughout
STAT_KEYS = ("int", "str", "agi", "wis", "luck")

# ═══════════════════════════════════════════
# ITEM GENERATION CONSTANTS
# ═══════════════════════════════════════════

# Luck bonus per point for rarity roll
RARITY_LUCK_MULT = 1.5

# Floor bonus for rarity roll
RARITY_FLOOR_MULT = 0.8

# Loot buff bonuses for rarity roll
RARITY_NIMBLE_FINGERS_BONUS = 20
RARITY_LOOTER_INST_BONUS = 10

# Floor scaling factor for item stats: fs = 1 + (floor-1) * ITEM_FLOOR_SCALING
ITEM_FLOOR_SCALING = 0.06

# Bonus stat random range: (BONUS_STAT_BASE + random() * BONUS_STAT_RANGE) * mul * fs
BONUS_STAT_BASE = 2
BONUS_STAT_RANGE = 4

# Cursed debuff range: ceil((CURSED_DEBUFF_BASE + random() * CURSED_DEBUFF_RANGE) * fs)
CURSED_DEBUFF_BASE = 3
CURSED_DEBUFF_RANGE = 5

# ═══════════════════════════════════════════
# STAT DERIVATION FORMULAS
# ═══════════════════════════════════════════

# Enemy scaling: ls = 1 + (floor - 1) * ENEMY_FLOOR_SCALING
ENEMY_FLOOR_SCALING = 0.08

# Enemy m_def = defense * ENEMY_MDEF_RATIO
ENEMY_MDEF_RATIO = 0.8

# Player ATK = ATK_BASE + str * ATK_STR_MULT + bonus_atk
ATK_BASE = 5
ATK_STR_MULT = 0.8

# Player DEF = DEF_BASE + wis * DEF_WIS_MULT + str * DEF_STR_MULT + bonus_def
DEF_BASE = 2
DEF_WIS_MULT = 0.3
DEF_STR_MULT = 0.3

# Player MDEF = MDEF_BASE + wis * MDEF_WIS_MULT + int * MDEF_INT_MULT
MDEF_BASE = 3
MDEF_WIS_MULT = 0.6
MDEF_INT_MULT = 0.3

# Player CRIT = CRIT_BASE + agi * CRIT_AGI_MULT
CRIT_BASE = 5
CRIT_AGI_MULT = 1.5

# Player EVA = EVA_BASE + agi * EVA_AGI_MULT
EVA_BASE = 3
EVA_AGI_MULT = 1.2

# Accuracy formula: min(ACC_MAX, max(ACC_MIN, ACC_BASE + agi * ACC_AGI_MULT))
ACC_BASE = 90
ACC_MIN = 50
ACC_MAX = 98
ACC_AGI_MULT = 0.5

# Max HP formula: HP_BASE + hp_per_level * (level-1) + str * HP_STR_MULT + bonus_hp
HP_STR_MULT = 2.5

# ═══════════════════════════════════════════
# DAMAGE FORMULA CONSTANTS
# ═══════════════════════════════════════════

# Secondary stat contribution: sv * SECONDARY_STAT_CONTRIBUTION
SECONDARY_STAT_CONTRIBUTION = 0.8

# Luck damage variance: multiplied by 1 + luck * LUCK_DMG_VARIANCE
# (already defined above as 0.005)

# Crit multiplier formula: CRIT_BASE_MULT + luck * CRIT_LUCK_MULT
CRIT_LUCK_MULT = 0.01

# Retribution counter-attack: atk * COUNTER_ATTACK_MULT
COUNTER_ATTACK_MULT = 0.30

# ═══════════════════════════════════════════
# SHOP CONSTANTS
# ═══════════════════════════════════════════

SHOP_ITEM_COUNT = 4
SHOP_BASE_PRICE = 10
SHOP_RARITY_PRICE_MULT = 8
SHOP_RANDOM_PRICE_MAX = 10

# ═══════════════════════════════════════════
# HEAL SKILL CONSTANTS
# ═══════════════════════════════════════════

# Missing HP heal fraction (Leng's Comfort)
HEAL_MISSING_HP_FRAC = 0.6

# Various heal fractions by skill name
HEAL_WIS15_FRAC = 0.15
HEAL_WIS30_FRAC = 0.30
HEAL_WIS20_FRAC = 0.20
HEAL_WIS25_FRAC = 0.25
HEAL_TITAN_RESIL_FRAC = 0.40
HEAL_DEVOUR_FRAC = 0.15
HEAL_MEDITATION_FRAC = 0.20
HEAL_DARK_REGEN_FRAC = 0.30
HEAL_SECOND_WIND_FRAC = 0.20
HEAL_NIMBLE_RECOV_FRAC = 0.25

# Madness costs for heal/shield skills
MADNESS_COST_HEAVY = 25
MADNESS_COST_MAJOR = 20
MADNESS_COST_MEDIUM = 15
MADNESS_COST_STANDARD = 10
MADNESS_COST_LIGHT = 8
MADNESS_COST_MINOR = 5
MADNESS_COST_TINY = 3

# Rage HP cost
BUFF_RAGE_HP_PCT = 0.12

# Warlord HP cost
BUFF_WARLORD_HP_PCT = 0.20

# Stat boost amounts for buff skills
BUFF_STAT_BOOST_TINY = 1
BUFF_STAT_BOOST_MINOR = 3
BUFF_STAT_BOOST_SMALL = 4
BUFF_STAT_BOOST_MEDIUM = 5
BUFF_STAT_BOOST_LARGE = 6
BUFF_STAT_BOOST_MAJOR = 7

# ═══════════════════════════════════════════
# BUFF SKILL CONSTANTS
# ═══════════════════════════════════════════

# Blood Ritual HP cost
BUFF_BLOOD_RITUAL_HP_PCT = 0.12

# Dark Pact HP cost
BUFF_DARK_PACT_HP_PCT = 0.15

# Pallid Mask HP cost
BUFF_PALLID_MASK_HP_PCT = 0.15

# Stat swap conversion factor
BUFF_STAT_SWAP_FACTOR = 0.5

# Copy attack power multiplier
BUFF_COPY_ATTACK_MULT = 0.5

# Eldritch Bargain heal fraction
BUFF_ELDRITCH_BARGAIN_HEAL_FRAC = 0.5

# ═══════════════════════════════════════════
# EVENT/TRAP EFFECT CONSTANTS
# ═══════════════════════════════════════════

EVENT_GOLD_REWARD = 15
EVENT_ROB_GOLD = 20
EVENT_OFFER_GOLD_COST = 20
EVENT_SHOP_ITEMS_MIN_FLOOR = 3
EVENT_TRAP_MIN_FLOOR = 2

# Deface event heal / trap attack damage fraction
EVENT_DEFACE_HEAL_PCT = 0.2
EVENT_DRINK_HEAL_PCT = 0.3
EVENT_DRINK_POISON_PCT = 0.2
EVENT_RATS_DAMAGE_PCT = 0.1

# ═══════════════════════════════════════════
# VISUAL DATA — Sprite & Icon mappings
# ═══════════════════════════════════════════

# Maps enemy names to their ASCII sprite keys
ENEMY_SPRITES = {
    "The All-Seeing Mass": "monster1",
    "The Skull Bearer": "monster3",
    "Storm Spawn": "monster4",
    "Carcosan Seer": "monster5",
    "Ember Horror": "monster6",
    "Hastur, The Spiral Beyond": "boss",
}

# Maps class ids to their sprite filenames
CLASS_SPRITES = {
    "scholar": "transparent-Int-basedClass",
    "brute": "transparent-Strenght-basedClass",
    "warden": "wis-character",
    "shadowblade": "transparent-Agi-basedClass",
    "mad_prophet": "transparent-luck-basedClass",
}

# Class display icons
CLASS_ICONS = {
    "scholar": "📖",
    "brute": "⚔",
    "warden": "🛡",
    "shadowblade": "🗡",
    "mad_prophet": "👁",
}

# Stat icon filenames (for rendering in stats screen / skill buttons)
STAT_ICONS = {
    "int": "Intelligence_Icon",
    "str": "Strenght_Icon",
    "agi": "Agility_Icon",
    "wis": "Wisdom_Icon",
    "luck": "Luck_Icon",
}
