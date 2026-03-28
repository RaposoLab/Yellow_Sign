"""Item generation: rarity determination and random item creation."""

import random
import math
from data import RARITY_DATA, CURSED_DEBUFFS, ITEM_PREFIXES, WEAPON_TEMPLATES, ARMOR_TEMPLATES, ACCESSORY_TEMPLATES, BOOTS_TEMPLATES, RING_TEMPLATES
from engine.models import Item

def determine_rarity(floor, luck, buffs=None):
    r = random.random() * 100 + (luck - 5) * 1.5 + floor * 0.8
    # Loot quality buffs increase rarity chances
    if buffs:
        if buffs.get("nimbleFingers", 0) > 0:
            r += 20  # +20% effective rarity roll
        elif buffs.get("looterInst", 0) > 0:
            r += 10  # +10% effective rarity roll
    if r >= 96:
        return 4
    elif r >= 80:
        return 3
    elif r >= 55:
        return 2
    return 1
def generate_item(floor, item_type=None, luck=5, buffs=None):
    """Generate a random item."""
    rarity = determine_rarity(floor, luck, buffs)
    rd = RARITY_DATA[rarity]
    fs = 1 + (floor - 1) * 0.06

    prefix = random.choice(ITEM_PREFIXES[rarity])

    # Choose template
    all_templates = {
        "weapon": WEAPON_TEMPLATES,
        "armor": ARMOR_TEMPLATES,
        "accessory": ACCESSORY_TEMPLATES,
        "boots": BOOTS_TEMPLATES,
        "ring": RING_TEMPLATES,
    }

    if item_type and item_type in all_templates:
        pool = all_templates[item_type]
    else:
        pool = []
        for templates in all_templates.values():
            pool.extend(templates)

    template = random.choice(pool)
    slot = template["slot"]
    if slot == "ring":
        slot = random.choice(["ringL", "ringR"])

    # Build stats
    stats = {}
    for k, v in template["base"].items():
        stats[k] = math.ceil(v * rd["stat_mul"] * fs)

    # Random bonus stats
    bonus_count = rd["stat_range"][0] + random.randint(0, rd["stat_range"][1] - rd["stat_range"][0])
    used = set(stats.keys())
    pool_shuffled = list(template["bonus_pool"])
    random.shuffle(pool_shuffled)
    all_stat_keys = ["int", "str", "agi", "wis", "luck", "atk", "def", "hp"]

    for i in range(bonus_count):
        if i < len(pool_shuffled):
            sk = pool_shuffled[i]
        else:
            available = [k for k in all_stat_keys if k not in used]
            sk = random.choice(available) if available else random.choice(all_stat_keys)
        used.add(sk)
        stats[sk] = stats.get(sk, 0) + math.ceil((2 + random.random() * 4) * rd["stat_mul"] * fs)

    # Cursed debuffs
    debuffs = None
    if rarity == 4:
        debuffs = {}
        dc = 1 + random.randint(0, 1)
        sd = list(CURSED_DEBUFFS)
        random.shuffle(sd)
        for i in range(dc):
            debuffs[sd[i]["stat"]] = math.ceil((3 + random.random() * 5) * fs)

    return Item(f"{prefix} {template['name']}", slot, stats, rarity, debuffs)
