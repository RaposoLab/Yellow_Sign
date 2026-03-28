"""
THE KING IN YELLOW — Game Data Package
All classes, skills, enemies, items, events, and game constants.
"""
from data.constants import MAX_ACTIVE_SKILLS, ENEMY_SPRITES, CLASS_SPRITES, CLASS_ICONS, STAT_ICONS
from data.classes import CLASSES
from data.enemies import ENEMIES, BOSS
from data.items import RARITY_DATA, CURSED_DEBUFFS, ITEM_PREFIXES, WEAPON_TEMPLATES, ARMOR_TEMPLATES, ACCESSORY_TEMPLATES, BOOTS_TEMPLATES, RING_TEMPLATES
from data.events import EVENTS, TRAPS
from data.narratives import FLOOR_NARRATIVES, PATH_TEMPLATES
from data.buff_debuff_data import EFFECT_REGISTRY, get_effect_info
