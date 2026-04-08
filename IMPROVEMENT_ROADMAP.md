# Code Quality Improvement Roadmap

## Status: ✅ Priority 1 COMPLETE

**Completed in commit:** `e7e2d1e`
- ✅ Fixed 4 division-by-zero risks
- ✅ Added comprehensive docstrings to `engine/damage.py` (7 functions)
- ✅ Improved type hints in `engine/damage.py`

---

## Priority 2: Type Hints for Core Engine Functions

### Goal
Add type hints to all core engine functions to catch bugs early during limb/madness system implementation.

### Files to Update

#### 1. `engine/combat.py` (~30 min)
Functions needing type hints:
- `start_combat(state: GameState, is_boss: bool = False) -> None` ✓ (already typed)
- `_get_enemy_intent_message(skill: Dict[str, Any]) -> str` ✓ (already typed)
- `enemy_turn(state: GameState) -> List[Tuple[str, str]]` ✓ (already typed)
- `check_boss_phase(state: GameState) -> List[Tuple[str, str]]` ✓ (already typed)
- `combat_run_attempt(state: GameState) -> bool` ✓ (already typed)

**Status:** ✅ Already well-typed!

#### 2. `engine/skills.py` (~1 hour)
Functions needing type hints:
- All `_calc_heal_*` functions → `Callable[[GameState, Skill], int]`
- All `_apply_shield_*` functions → `Callable[[GameState, Skill], Optional[int]]`
- All `_apply_buff_*` functions → `Callable[[GameState, Skill], Optional[Dict[str, Any]]]`
- `use_skill(state: GameState, skill: Skill) -> List[Tuple[str, str]]`

**Action Plan:**
```python
# Example transformation
def _calc_heal_int2_buff(state: GameState, skill: Skill) -> int:
    """Heal based on INT stat + buff INT by 3."""
    h = int(state.stats["int"] * 2)
    state.base_stats["int"] += 3
    state.recalc_stats()
    return h
```

#### 3. `engine/status_effects.py` (~30 min)
Functions to type:
- `apply_status_effect_on_player(...)` 
- `apply_status_player(...)`
- `process_status_effects(...)`
- `process_player_status_effects(...)`
- `tick_player_buffs(...)`

#### 4. `engine/models.py` (~45 min)
Key classes/methods to verify:
- `Enemy.__init__()` 
- `CombatState.__init__()`
- `GameState.recalc_stats()`
- `GameState.add_madness(amount: int) -> bool`
- `GameState.check_level_up() -> bool`
- `PlayerClass.__init__()`

### Estimated Time: 2-3 hours
### Benefit: Catch type-related bugs during limb loss/madness overhaul

---

## Priority 3: Code Quality Improvements

### 3A. Rename camelCase to snake_case in `engine/skills.py` (~1 hour)

**Issue:** 31 private functions use camelCase instead of Python's snake_case convention

**Examples to rename:**
- `_calcHealInt2Buff` → `_calc_heal_int2_buff` (already correct!)
- `_applyShieldDef` → `_apply_shield_def` (already correct!)
- `_applyBuffCritUp` → `_apply_buff_crit_up` (already correct!)

**Action:** Verify all function names follow snake_case convention

### 3B. Add Docstrings to Remaining Functions (~2 hours)

**Current coverage:** ~26% (77/293 functions)
**Target:** 80%+ coverage

**Priority files:**
1. `engine/skills.py` - ~50 heal/shield/buff calculators
2. `engine/status_effects.py` - status effect handlers
3. `engine/items.py` - item generation logic
4. `engine/world.py` - dungeon generation

**Template:**
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """One-line summary.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this happens (if applicable)
    """
```

### 3C. Implement Validation Layer (~1.5 hours)

**Goal:** Ensure game state consistency before major refactors

**Implementation:**
```python
# engine/validation.py (new file)
from typing import List, Tuple
from engine.models import GameState

def validate_game_state(state: GameState) -> List[str]:
    """Validate game state consistency.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    # HP validation
    if state.hp < 0:
        errors.append(f"HP below 0: {state.hp}")
    if state.hp > state.max_hp:
        errors.append(f"HP ({state.hp}) exceeds max_hp ({state.max_hp})")
    
    # Madness validation
    if not 0 <= state.madness <= 100:
        errors.append(f"Madness out of range: {state.madness}")
    
    # Shield/barrier validation
    if state.shield < 0:
        errors.append(f"Negative shield: {state.shield}")
    if state.barrier < 0:
        errors.append(f"Negative barrier: {state.barrier}")
    
    # Buff duration validation
    for buff_name, duration in state.buffs.items():
        if duration < 0:
            errors.append(f"Negative buff duration for {buff_name}: {duration}")
    
    return errors

def assert_valid_state(state: GameState) -> None:
    """Assert game state is valid, raise AssertionError if not."""
    errors = validate_game_state(state)
    if errors:
        raise AssertionError("Game state invalid:\\n" + "\\n".join(errors))
```

**Integration points:**
- End of player turn
- End of enemy turn
- After skill usage
- Before save game

### 3D. Add Unit Tests for Edge Cases (~1 hour)

**New test scenarios:**
```python
# tests/test_edge_cases.py
def test_zero_max_hp_damage_calculation():
    """Ensure no division by zero when max_hp is 0."""
    # Test _base_damage with state.max_hp = 0
    
def test_negative_stat_values():
    """Ensure negative stats don't break calculations."""
    
def test_extreme_madness_values():
    """Test madness at 0 and 100 boundaries."""
    
def test_limb_loss_edge_cases():
    """Test losing multiple limbs simultaneously."""
```

---

## Implementation Timeline

### Week 1 (Before Combat Overhaul)
- [x] **Priority 1:** Fix division-by-zero bugs ✅
- [ ] **Priority 2:** Add type hints to skills.py, status_effects.py
- [ ] **Priority 3C:** Implement validation layer

### Week 2 (During Combat Overhaul)
- [ ] **Priority 3A:** Verify snake_case naming
- [ ] **Priority 3B:** Add docstrings to new limb/madness systems
- [ ] **Priority 3D:** Add edge case tests

### Week 3 (Polish)
- [ ] Run mypy for type checking
- [ ] Achieve 80%+ docstring coverage
- [ ] Full test suite pass with new combat system

---

## Tools Recommendation

### Static Analysis
```bash
# Install
pip install mypy black flake8 pylint

# Type checking
mypy engine/ --strict

# Code formatting
black engine/ screens/ data.py

# Linting
flake8 engine/ --max-line-length=100
pylint engine/ --disable=C0114,C0115,C0116
```

### Pre-commit Hooks (Optional)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/python/mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
```

---

## Success Metrics

- [x] Zero division-by-zero errors ✅
- [ ] 100% of public functions have type hints
- [ ] 80%+ docstring coverage
- [ ] All 271 tests still passing + new edge case tests
- [ ] mypy passes with no errors
- [ ] Validation layer catches state inconsistencies

---

## Notes for Limb Loss System Implementation

When implementing the limb loss system from your roadmap, ensure:

1. **Type Safety:** Use enums for limb types
   ```python
   from enum import Enum
   
   class LimbType(Enum):
       LEFT_ARM = "left_arm"
       RIGHT_ARM = "right_arm"
       LEFT_LEG = "left_leg"
       RIGHT_LEG = "right_leg"
   ```

2. **Validation:** Add limb-specific validations
   ```python
   def validate_limbs(state: GameState) -> List[str]:
       errors = []
       if len(state.lost_limbs) >= 4:
           errors.append("All limbs lost - game over condition")
       # Check ability slot consistency
       return errors
   ```

3. **Documentation:** Document limb loss effects per class
   ```python
   def lose_limb(state: GameState, limb: LimbType) -> List[str]:
       """Remove a limb and apply associated debuffs.
       
       Args:
           state: Current game state
           limb: The limb type being lost
           
       Returns:
           List of log messages describing effects
           
       Side Effects:
           - Removes abilities requiring the limb
           - Reduces item slots if arm lost
           - May trigger game over if critical limbs lost
       """
   ```

---

**Last Updated:** After commit `e7e2d1e`
**Next Action:** Begin Priority 2 (type hints for skills.py)
