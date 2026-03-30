"""
THE KING IN YELLOW — Game Engine Package
Core game logic: models, combat, leveling, items, floor progression.
"""
from engine.models import Item, Skill, StatusEffect, CombatState, Enemy, GameState, has_status, apply_status
from engine.items import determine_rarity, generate_item
from engine.damage import (
    calc_player_damage, calc_preview_damage,
    apply_damage_to_enemy, apply_damage_to_player,
    _base_damage, _get_buff_defense_bonus, _get_buff_evasion_bonus,
)
from engine.status_effects import (
    apply_status_effect_on_player, apply_status_player,
    process_status_effects, process_player_status_effects,
    tick_player_buffs,
)
from engine.combat import (
    start_combat, enemy_turn, combat_run_attempt, check_boss_phase,
    _get_enemy_intent_message,
)
from engine.skills import player_use_skill
from engine.world import generate_paths, advance_floor, get_floor_narrative, resolve_event, resolve_trap, generate_shop, buy_shop_item
