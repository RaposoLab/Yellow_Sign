"""Item generation: rarity determination and random item creation."""

import random
import math
from typing import Optional, Dict, Any, TypedDict, Tuple, cast

from data import (
    RARITY_DATA,
    CURSED_DEBUFFS,
    ITEM_PREFIXES,
    WEAPON_TEMPLATES,
    ARMOR_TEMPLATES,
    ACCESSORY_TEMPLATES,
    BOOTS_TEMPLATES,
    RING_TEMPLATES,
    RARITY_LUCK_MULT,
    RARITY_FLOOR_MULT,
    RARITY_NIMBLE_FINGERS_BONUS,
    RARITY_LOOTER_INST_BONUS,
    ITEM_FLOOR_SCALING,
    BONUS_STAT_BASE,
    BONUS_STAT_RANGE,
    CURSED_DEBUFF_BASE,
    CURSED_DEBUFF_RANGE,
)
from engine.models import Item


class RarityData(TypedDict):
    """TypedDict for RARITY_DATA entries."""

    name: str
    color: str
    stat_range: Tuple[int, int]
    stat_mul: float


class CursedDebuff(TypedDict):
    """TypedDict for CURSED_DEBUFFS entries."""

    stat: str
    name: str


class ItemTemplate(TypedDict):
    """TypedDict for equipment template entries."""

    name: str
    slot: str
    base: Dict[str, int]
    bonus_pool: list


def determine_rarity(floor: int, luck: int, buffs: Optional[Dict[str, int]] = None) -> int:
    """Determine item rarity based on floor, luck, and active loot buffs."""
    r = random.random() * 100 + (luck - 5) * RARITY_LUCK_MULT + floor * RARITY_FLOOR_MULT
    if buffs:
        if buffs.get("nimbleFingers", 0) > 0:
            r += RARITY_NIMBLE_FINGERS_BONUS
        elif buffs.get("looterInst", 0) > 0:
            r += RARITY_LOOTER_INST_BONUS
    if r >= 96:
        return 4
    elif r >= 80:
        return 3
    elif r >= 55:
        return 2
    return 1


def generate_item(
    floor: int,
    item_type: Optional[str] = None,
    luck: int = 5,
    buffs: Optional[Dict[str, int]] = None,
) -> Item:
    """Generate a random item."""
    rarity = determine_rarity(floor, luck, buffs)
    rd = cast(RarityData, RARITY_DATA[rarity])
    fs = 1 + (floor - 1) * ITEM_FLOOR_SCALING

    prefix = random.choice(ITEM_PREFIXES[rarity])

    all_templates: Dict[str, list] = {
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
    t = cast(ItemTemplate, template)
    slot: str = t["slot"]
    if slot == "ring":
        slot = random.choice(["ringL", "ringR"])

    stats: Dict[str, int] = {}
    for k, v in t["base"].items():
        stats[k] = math.ceil(v * rd["stat_mul"] * fs)

    bonus_count = rd["stat_range"][0] + random.randint(0, rd["stat_range"][1] - rd["stat_range"][0])
    used = set(stats.keys())
    pool_shuffled = list(t["bonus_pool"])
    random.shuffle(pool_shuffled)
    all_stat_keys = ["int", "str", "agi", "wis", "luck", "atk", "def", "hp"]

    for i in range(bonus_count):
        if i < len(pool_shuffled):
            sk = pool_shuffled[i]
        else:
            available = [k for k in all_stat_keys if k not in used]
            sk = random.choice(available) if available else random.choice(all_stat_keys)
        used.add(sk)
        stats[sk] = stats.get(sk, 0) + math.ceil(
            (BONUS_STAT_BASE + random.random() * BONUS_STAT_RANGE) * rd["stat_mul"] * fs
        )

    debuffs: Optional[Dict[str, int]] = None
    if rarity == 4:
        debuffs = {}
        dc = 1 + random.randint(0, 1)
        sd = list(CURSED_DEBUFFS)
        random.shuffle(sd)
        for i in range(dc):
            cd = cast(CursedDebuff, sd[i])
            debuffs[cd["stat"]] = math.ceil((CURSED_DEBUFF_BASE + random.random() * CURSED_DEBUFF_RANGE) * fs)

    return Item(f"{prefix} {t['name']}", slot, stats, rarity, debuffs)
