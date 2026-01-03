import json
import os
from typing import Optional

DATA_FILE = "data.json"

DEFAULT_DATA = {
    "linklog_channel": None,
    "flagged_users": [],
    "cooldown": 0,
    "guild_settings": {}
}

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                for key, value in DEFAULT_DATA.items():
                    if key not in data:
                        data[key] = value
                return data
        except (json.JSONDecodeError, IOError):
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()

def save_data(data: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_linklog_channel(guild_id: int) -> Optional[int]:
    data = load_data()
    guild_settings = data.get("guild_settings", {}).get(str(guild_id), {})
    channel_id = guild_settings.get("linklog_channel")
    if channel_id:
        return int(channel_id)
    return None

def set_linklog_channel(guild_id: int, channel_id: int) -> None:
    data = load_data()
    if "guild_settings" not in data:
        data["guild_settings"] = {}
    if str(guild_id) not in data["guild_settings"]:
        data["guild_settings"][str(guild_id)] = {}
    data["guild_settings"][str(guild_id)]["linklog_channel"] = str(channel_id)
    save_data(data)

def get_cooldown(guild_id: int) -> int:
    data = load_data()
    guild_settings = data.get("guild_settings", {}).get(str(guild_id), {})
    return guild_settings.get("cooldown", 0)

def set_cooldown(guild_id: int, seconds: int) -> None:
    data = load_data()
    if "guild_settings" not in data:
        data["guild_settings"] = {}
    if str(guild_id) not in data["guild_settings"]:
        data["guild_settings"][str(guild_id)] = {}
    data["guild_settings"][str(guild_id)]["cooldown"] = seconds
    save_data(data)

def is_user_flagged(guild_id: int, user_id: int) -> bool:
    data = load_data()
    guild_settings = data.get("guild_settings", {}).get(str(guild_id), {})
    flagged = guild_settings.get("flagged_users", [])
    return str(user_id) in flagged

def flag_user(guild_id: int, user_id: int) -> bool:
    data = load_data()
    if "guild_settings" not in data:
        data["guild_settings"] = {}
    if str(guild_id) not in data["guild_settings"]:
        data["guild_settings"][str(guild_id)] = {}
    if "flagged_users" not in data["guild_settings"][str(guild_id)]:
        data["guild_settings"][str(guild_id)]["flagged_users"] = []
    
    if str(user_id) in data["guild_settings"][str(guild_id)]["flagged_users"]:
        return False
    
    data["guild_settings"][str(guild_id)]["flagged_users"].append(str(user_id))
    save_data(data)
    return True

def unflag_user(guild_id: int, user_id: int) -> bool:
    data = load_data()
    guild_settings = data.get("guild_settings", {}).get(str(guild_id), {})
    flagged = guild_settings.get("flagged_users", [])
    
    if str(user_id) not in flagged:
        return False
    
    data["guild_settings"][str(guild_id)]["flagged_users"].remove(str(user_id))
    save_data(data)
    return True

def get_flagged_users(guild_id: int) -> list:
    data = load_data()
    guild_settings = data.get("guild_settings", {}).get(str(guild_id), {})
    return guild_settings.get("flagged_users", [])
