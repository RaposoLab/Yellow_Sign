"""Enemy definitions and boss data."""

# ═══════════════════════════════════════════
# ENEMIES
# ═══════════════════════════════════════════

ENEMIES = [
    {
        "name": "The All-Seeing Mass",
        "type": "Eldritch Horror",
        "desc": "A writhing sphere of eyes and tentacles. It sees everything.",
        "hp_mult": 1.2,
        "atk_mult": 1.0,
        "def_mult": 0.9,
        "skills": [
            {"name": "Tentacle Lash", "type": "physical", "power": 1.3},
            {"name": "Gaze of Madness", "type": "magic_debuff", "power": 1.0, "effect": "blinded", "duration": 2},
            {"name": "Regenerate", "type": "self_heal", "power": 0.06},
        ],
        "level_range": [1, 6],
    },
    {
        "name": "The Skull Bearer",
        "type": "Undead Horror",
        "desc": "A towering figure draped in bone. Each skull whispers a name.",
        "hp_mult": 1.0,
        "atk_mult": 1.3,
        "def_mult": 1.0,
        "skills": [
            {"name": "Bone Crush", "type": "physical", "power": 1.5},
            {"name": "Skull Storm", "type": "physical_debuff", "power": 1.2, "effect": "shocked", "duration": 2},
            {"name": "Life Drain", "type": "magic", "power": 1.0, "lifesteal": 0.3},
        ],
        "level_range": [3, 10],
    },
    {
        "name": "Storm Spawn",
        "type": "Elemental Aberration",
        "desc": "Lightning given form and malice. The air crackles around it.",
        "hp_mult": 0.8,
        "atk_mult": 1.4,
        "def_mult": 0.7,
        "skills": [
            {"name": "Lightning Bolt", "type": "magic", "power": 1.6},
            {"name": "Static Charge", "type": "magic_debuff", "power": 1.0, "effect": "shocked", "duration": 2},
            {"name": "Thunder Roar", "type": "physical_debuff", "power": 1.1, "effect": "weakened", "duration": 2},
        ],
        "level_range": [5, 12],
    },
    {
        "name": "Carcosan Seer",
        "type": "Humanoid Cultist",
        "desc": "A robed figure whose eyes burn with yellow fire. They know what you're thinking.",
        "hp_mult": 0.7,
        "atk_mult": 1.5,
        "def_mult": 0.8,
        "skills": [
            {"name": "Eldritch Bolt", "type": "magic", "power": 1.8},
            {"name": "Mind Rend", "type": "magic_debuff", "power": 1.2, "effect": "petrified", "duration": 2},
            {"name": "Dark Barrier", "type": "self_heal", "power": 0.08},
        ],
        "level_range": [7, 15],
    },
    {
        "name": "Ember Horror",
        "type": "Fire Elemental",
        "desc": "A being of living flame that screams as it burns. The smell of charred flesh lingers.",
        "hp_mult": 0.9,
        "atk_mult": 1.5,
        "def_mult": 0.8,
        "skills": [
            {"name": "Flame Strike", "type": "magic", "power": 1.7},
            {"name": "Inferno", "type": "magic_debuff", "power": 1.3, "effect": "burning", "duration": 3},
            {"name": "Cauterize", "type": "self_heal", "power": 0.07},
        ],
        "level_range": [10, 18],
    },
]

BOSS = {
    "name": "Hastur, The Spiral Beyond",
    "type": "???",
    "desc": "The Tattered King rises. Reality unravels at his presence.",
    "hp_mult": 4.0,
    "atk_mult": 1.6,
    "def_mult": 1.4,
    "skills": [
        {"name": "Yellow Sign", "type": "magic_debuff", "power": 1.5, "effect": "petrified", "duration": 3},
        {"name": "Carcosa's Embrace", "type": "magic", "power": 2.2},
        {"name": "The King's Madness", "type": "magic_debuff", "power": 1.3, "effect": "shocked", "duration": 2},
        {"name": "Tattered Reality", "type": "magic", "power": 2.8},
        {"name": "Restoration", "type": "self_heal", "power": 0.08},
        {"name": "Pallid Mask", "type": "magic_debuff", "power": 1.0, "effect": "blinded", "duration": 3},
    ],
    "level_range": [20, 20],
}
