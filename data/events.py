"""Floor events and trap definitions."""

# ═══════════════════════════════════════════
# FLOOR EVENTS
# ═══════════════════════════════════════════

EVENTS = [
    {
        "title": "Whispers in the Dark",
        "icon": "?",
        "text": "A voice speaks from nowhere. It offers forbidden knowledge for sanity.",
        "outcomes": [
            {"text": "Accept (INT+2, +10 Madness)", "effect": "gain_int_2_mad_10"},
            {"text": "Refuse", "effect": "nothing"},
            {"text": "Reason (50%: WIS+2 or +15 MAD)", "effect": "reason_50"},
        ],
    },
    {
        "title": "The Yellow Sign",
        "icon": "!",
        "text": "The Yellow Sign carved into the wall. Looking too long makes thoughts slippery.",
        "outcomes": [
            {"text": "Study (STR+2, +8 Madness)", "effect": "gain_str_2_mad_8"},
            {"text": "Avert eyes (-5 Madness)", "effect": "mad_minus_5"},
            {"text": "Deface (50%: Heal 20% or +12 MAD)", "effect": "deface_50"},
        ],
    },
    {
        "title": "Abandoned Laboratory",
        "icon": "#",
        "text": "Shattered beakers and strange chemicals. Some might still be useful... or poisonous.",
        "outcomes": [
            {"text": "Drink (60%: Heal 30% or take 20%)", "effect": "drink_60"},
            {"text": "Search (+15 gold)", "effect": "gold_15"},
            {"text": "Leave it", "effect": "nothing"},
        ],
    },
    {
        "title": "The Survivor",
        "icon": "+",
        "text": 'Another patient, barely alive. They mumble about "the way out."',
        "outcomes": [
            {"text": "Help (+10 MAD, receive item)", "effect": "help_survivor"},
            {"text": "Take from them (+20 gold, +5 MAD)", "effect": "rob_survivor"},
            {"text": "Walk away", "effect": "nothing"},
        ],
    },
    {
        "title": "Shrine to Hastur",
        "icon": "-",
        "text": "A crude altar of yellow cloth and bone. The air hums with power.",
        "outcomes": [
            {"text": "Pray (Full heal, +15 MAD)", "effect": "pray_full_heal"},
            {"text": "Desecrate (AGI+3, +10 MAD)", "effect": "desecrate"},
            {"text": "Offer 20g (WIS+3)", "effect": "offer_gold"},
        ],
    },
    {
        "title": "Rats... or Are They?",
        "icon": "=",
        "text": "A swarm of rats watches with intelligent eyes. One speaks your name.",
        "outcomes": [
            {"text": "Listen (Random stat+1, +3 MAD)", "effect": "listen_rats"},
            {"text": "Flee (+5 MAD)", "effect": "mad_5"},
            {"text": "Attack (-10% HP, STR+1)", "effect": "attack_rats"},
        ],
    },
]

TRAPS = [
    {
        "name": "Collapsing Floor",
        "desc": "The floor gives way!",
        "outcomes": [
            {"chance": 0.5, "text": "Catch yourself! 10% damage.", "dmg_pct": 0.1, "madness": 0},
            {"chance": 1.0, "text": "Fall! 25% damage.", "dmg_pct": 0.25, "madness": 5},
        ],
    },
    {
        "name": "Yellow Mist",
        "desc": "Thick yellow fog whispers things.",
        "outcomes": [
            {"chance": 0.4, "text": "Hold breath. Safe.", "dmg_pct": 0, "madness": 0},
            {"chance": 1.0, "text": "Mist seeps in. +12 MAD.", "dmg_pct": 0, "madness": 12},
        ],
    },
    {
        "name": "Trap of Madness",
        "desc": "Walls covered in maddening symbols.",
        "outcomes": [
            {"chance": 0.3, "text": "Steel your mind. Resist.", "dmg_pct": 0, "madness": 0},
            {"chance": 1.0, "text": "Symbols burn in. +18 MAD.", "dmg_pct": 0, "madness": 18},
        ],
    },
]


