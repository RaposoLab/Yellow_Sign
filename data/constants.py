"""Game constants and sprite/icon mappings."""

MAX_ACTIVE_SKILLS = 4

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

