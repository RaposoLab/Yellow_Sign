"""Floor narratives and exploration path templates — loaded from JSON."""

import json
import os

_JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json")

def _load_json(filename):
    path = os.path.join(_JSON_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ═══════════════════════════════════════════
# FLOOR NARRATIVES
# ═══════════════════════════════════════════

FLOOR_NARRATIVES = _load_json("narratives.json")

# ═══════════════════════════════════════════
# PATH TYPES FOR EXPLORATION
# ═══════════════════════════════════════════

PATH_TEMPLATES = _load_json("paths.json")
