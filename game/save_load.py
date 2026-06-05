import json
import os
import time

SAVE_PATH = "save.json"


def save_game(time_sys, resources, areas, creatures, player_name=""):
    data = {
        "version":     1,
        "saved_at":    time.time(),
        "player_name": player_name,
        "time":        time_sys.to_dict(),
        "resources":   resources.to_dict(),
        "areas":       areas.to_dict(),
        "creatures":   creatures.to_dict(),
    }
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def load_game(time_sys, resources, areas, creatures):
    """Returns (success, player_name)."""
    if not os.path.exists(SAVE_PATH):
        return False, ""
    try:
        with open(SAVE_PATH) as f:
            data = json.load(f)
        time_sys.from_dict(data.get("time", {}))
        resources.from_dict(data.get("resources", {}))
        areas.from_dict(data.get("areas", {}))
        creatures.from_dict(data.get("creatures", {}))
        return True, data.get("player_name", "")
    except Exception as e:
        print(f"[save_load] Could not load save: {e}")
        return False, ""
