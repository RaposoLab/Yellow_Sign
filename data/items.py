"""Item system: rarities, prefixes, templates for all equipment slots."""

# ═══════════════════════════════════════════
# ITEM SYSTEM
# ═══════════════════════════════════════════

RARITY_DATA = {
    1: {"name": "Common", "color": "white", "stat_range": (1, 2), "stat_mul": 0.7},
    2: {"name": "Uncommon", "color": "green", "stat_range": (2, 3), "stat_mul": 1.0},
    3: {"name": "Rare", "color": "cyan", "stat_range": (3, 3), "stat_mul": 1.35},
    4: {"name": "Cursed", "color": "red", "stat_range": (2, 4), "stat_mul": 1.6},
}

CURSED_DEBUFFS = [
    {"stat": "str", "name": "Frailty"},
    {"stat": "int", "name": "Idiocy"},
    {"stat": "agi", "name": "Lethargy"},
    {"stat": "wis", "name": "Doubt"},
    {"stat": "luck", "name": "Misfortune"},
]

ITEM_PREFIXES = {
    1: ["Rusted", "Cracked", "Worn", "Faded", "Old"],
    2: ["Tainted", "Eldritch", "Whispering", "Forgotten", "Glowing"],
    3: ["Enchanted", "Void-touched", "Carcosan", "Arcane", "Mythic"],
    4: ["Cursed", "Bloodied", "Hollow", "Blighted", "Damned"],
}

WEAPON_TEMPLATES = [
    {"name": "Blade", "slot": "weapon", "base": {"atk": 5}, "bonus_pool": ["int", "str", "agi", "luck"]},
    {"name": "Tome", "slot": "weapon", "base": {"atk": 3, "int": 3}, "bonus_pool": ["int", "wis"]},
    {"name": "Cudgel", "slot": "weapon", "base": {"atk": 6, "str": 1}, "bonus_pool": ["str", "wis"]},
    {"name": "Dagger", "slot": "weapon", "base": {"atk": 4, "agi": 2}, "bonus_pool": ["agi", "luck"]},
    {"name": "Staff", "slot": "weapon", "base": {"atk": 3, "wis": 3}, "bonus_pool": ["wis", "int"]},
]

ARMOR_TEMPLATES = [
    {"name": "Robes", "slot": "armor", "base": {"def": 3, "int": 2}, "bonus_pool": ["int", "wis"]},
    {"name": "Chainmail", "slot": "armor", "base": {"def": 6, "str": 1}, "bonus_pool": ["str", "luck"]},
    {"name": "Leather", "slot": "armor", "base": {"def": 4, "agi": 2}, "bonus_pool": ["agi"]},
    {"name": "Mantle", "slot": "armor", "base": {"def": 4, "wis": 2}, "bonus_pool": ["wis", "int"]},
]

ACCESSORY_TEMPLATES = [
    {"name": "Brooch", "slot": "accessory", "base": {"def": 2, "int": 1}, "bonus_pool": ["int", "wis", "luck"]},
    {"name": "Cloak", "slot": "accessory", "base": {"def": 3, "agi": 1}, "bonus_pool": ["agi", "wis"]},
    {"name": "Sash", "slot": "accessory", "base": {"hp": 8, "str": 1}, "bonus_pool": ["str", "luck", "hp"]},
    {"name": "Talisman", "slot": "accessory", "base": {"wis": 2, "int": 1}, "bonus_pool": ["wis", "int", "luck"]},
]

BOOTS_TEMPLATES = [
    {"name": "Sandals", "slot": "boots", "base": {"agi": 3, "def": 1}, "bonus_pool": ["agi", "luck", "hp"]},
    {"name": "Greaves", "slot": "boots", "base": {"def": 3, "str": 1}, "bonus_pool": ["str", "agi"]},
    {"name": "Boots", "slot": "boots", "base": {"agi": 2, "def": 2}, "bonus_pool": ["agi", "wis"]},
    {"name": "Treads", "slot": "boots", "base": {"def": 2, "hp": 6}, "bonus_pool": ["str", "luck", "hp"]},
]

RING_TEMPLATES = [
    {"name": "Band", "slot": "ring", "base": {}, "bonus_pool": ["int", "str", "agi", "wis", "luck"]},
    {"name": "Seal", "slot": "ring", "base": {"def": 1}, "bonus_pool": ["wis", "int", "luck"]},
    {"name": "Signet", "slot": "ring", "base": {"atk": 2}, "bonus_pool": ["str", "agi", "luck"]},
    {"name": "Loop", "slot": "ring", "base": {"hp": 5}, "bonus_pool": ["luck", "wis", "hp"]},
]
