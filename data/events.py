"""Floor events and trap definitions — loaded from JSON."""

import json
import os

_JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json")

def _load_json(filename):
    path = os.path.join(_JSON_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ═══════════════════════════════════════════
# FLOOR EVENTS
# ═══════════════════════════════════════════

EVENTS = _load_json("events.json")

# ═══════════════════════════════════════════
# TRAPS
# ═══════════════════════════════════════════

TRAPS = _load_json("traps.json")
