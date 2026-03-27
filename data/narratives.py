"""Floor narratives and exploration path templates."""

# ═══════════════════════════════════════════
# FLOOR NARRATIVES
# ═══════════════════════════════════════════

FLOOR_NARRATIVES = [
    "The ground floor of the asylum. Flickering lights cast long shadows. Something scratched 'PH'NGLUI on the wall.",
    "The wards. Patients' cells stand open, empty. Wet footprints lead deeper inside.",
    "The infirmary. Medicine cabinets shattered. A yellow glow pulses from the operating theater.",
    "The basement. Pipes groan and hiss. The air tastes of copper and old prayers.",
    "Sub-level one. The architecture doesn't make sense anymore. Corridors bend wrong.",
    "The catacombs beneath. Ancient stonework meets modern concrete. Both are cracking.",
    "Deeper still. The walls are damp with something that isn't water. It smells of the sea.",
    "A vast chamber. Pillars of impossible height support a ceiling you cannot see.",
    "The walls here are carved with symbols that make your eyes hurt to look at.",
    "The Ritual Hall. Yellow banners hang from impossible heights. Candles burn without flame.",
    "The air vibrates. You can hear chanting in a language that predates humanity.",
    "The Threshold. Reality thins here. You can see through walls to places that shouldn't exist.",
    "Something is following you. You can hear it breathing when you stop moving.",
    "The corridors twist and fold. You've been walking in circles — or have you?",
    "Carcosa's influence grows. The yellow tint in everything is unmistakable now.",
    "The walls bleed light. Shadows move independently. The end is near.",
    "You can feel the King's presence. The air crackles with ancient power.",
    "The final corridors. Every step echoes with the weight of millennia.",
    "Carcosa's Gate. The walls are no longer walls. They breathe. They watch.",
    "The throne room of the King in Yellow. There is no escape but through.",
]


# ═══════════════════════════════════════════
# PATH TYPES FOR EXPLORATION
# ═══════════════════════════════════════════

PATH_TEMPLATES = [
    {"type": "combat", "icon": "!", "name": "Dark Passage", "desc": "Something stirs in the shadows",
     "desc2": "A creature lurks ahead. Steel yourself — blood will be spilled.", "hint": "Enemy", "weight": 3},
    {"type": "combat", "icon": "+", "name": "Blood Trail", "desc": "A trail of blood leads into the dark",
     "desc2": "Fresh crimson stains mark the floor. Something wounded — or something feeding.", "hint": "Enemy", "weight": 3},
    {"type": "combat", "icon": "~", "name": "Lurking Horror", "desc": "Eyes watch from the darkness",
     "desc2": "Dozens of unblinking eyes pierce the gloom. The beast is patient. You are not safe.", "hint": "Enemy", "weight": 2},
    {"type": "event", "icon": "?", "name": "Strange Sound", "desc": "An unearthly melody echoes",
     "desc2": "A haunting tune drifts through the corridors. Approach, and face the unknown.", "hint": "Unknown", "weight": 1},
    {"type": "event", "icon": "#", "name": "Forbidden Text", "desc": "A tome lies open, pages turning",
     "desc2": "Knowledge or madness — the pages whisper secrets no mortal should hear.", "hint": "Knowledge or madness", "weight": 1},
    {"type": "loot", "icon": "=", "name": "Supply Room", "desc": "An untouched closet, door ajar",
     "desc2": "Someone abandoned their belongings here. Take what you can — you will need it.", "hint": "Equipment", "weight": 1},
    {"type": "loot", "icon": "$", "name": "Offering", "desc": "Something glitters on a stone altar",
     "desc2": "An offering to forgotten gods. The treasure is yours — if you dare claim it.", "hint": "Equipment", "weight": 1},
    {"type": "rest", "icon": "-", "name": "Safe Haven", "desc": "A moment of calm in the storm",
     "desc2": "A rare sanctuary. Tend your wounds, clear your mind, or prepare your body.", "hint": "Healing", "weight": 1},
    {"type": "shop", "icon": "@", "name": "Mad Trader", "desc": "A figure deals in strange wares",
     "desc2": "Eyes wild, smile crooked. Their goods are real — the price, however, is never simple.", "hint": "Items", "weight": 1},
    {"type": "trap", "icon": "^", "name": "Suspicious Hallway", "desc": "Uneven floor, thick dread",
     "desc2": "The stones shift beneath your feet. Every step could be your last. Tread carefully.", "hint": "Danger", "weight": 1},
]
