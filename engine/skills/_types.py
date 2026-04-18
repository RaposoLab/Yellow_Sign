"""Shared type aliases for the skill handler system."""

from typing import Tuple, Dict, Any, Optional, Callable

from engine.models import Skill, GameState

# Type aliases used across all skill handler modules
LogEntry = Tuple[str, str]
HealCalcFn = Callable[[GameState, Skill], int]
ShieldCalcFn = Callable[[GameState, Skill], Optional[int]]
BuffApplyFn = Callable[[GameState, Skill], Optional[Dict[str, Any]]]
