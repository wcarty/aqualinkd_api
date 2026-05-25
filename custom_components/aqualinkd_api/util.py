from __future__ import annotations

import logging
import re
from typing import Any

_LOGGER = logging.getLogger(__name__)

def slugify(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower().replace("/", "_")
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in ("on", "true", "1", "enabled", "yes"):
            return True
        if cleaned in ("off", "false", "0", "disabled", "no"):
            return False
    return None


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().upper()
        for unit in ("%", "PPM", "RPM", "W", "F", "C", "V"):
            cleaned = cleaned.replace(unit, "")
        try:
            return float(cleaned.strip())
        except ValueError:
            # Fallback to regex to find the first numeric-looking part
            match = re.search(r"([-+]?\d*\.?\d+)", value)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    return None
            return None
    return None


def flatten_devices(data: dict[str, Any] | list[Any]) -> dict[str, dict[str, Any]]:
    """Normalize common AqualinkD /api/devices payload shapes into device dictionaries.

    The API shape varies by build/panel. This function is intentionally tolerant.
    """
    _LOGGER.debug("Flattening data type %s", type(data))
    
    source = data
    if isinstance(data, dict):
        if "devices" in data:
            source = data["devices"]
        elif "status" in data and isinstance(data["status"], dict):
            source = data["status"]
            
    devices: dict[str, dict[str, Any]] = {}
    
    # Helper to check if a name should be ignored
    def _is_ignored(name_or_id: str) -> bool:
        if not name_or_id:
            return False
        nl = str(name_or_id).lower()
        return "aux_b" in nl or "aux_v" in nl or "aux_s" in nl

    # Pre-process nested containers if they exist
    if isinstance(data, dict):
        for container in ("leds", "timers", "sensors"):
            if container in data and isinstance(data[container], dict):
                _LOGGER.debug("Extracting devices from nested container: %s", container)
                for k, v in data[container].items():
                    if _is_ignored(k):
                        continue
                    # Create a simple device entry from the container item
                    devices[str(k)] = {"name": k, "state": v}

    if isinstance(source, list):
        _LOGGER.debug("Processing list source with %d items", len(source))
        for item in source:
            if isinstance(item, dict):
                # Use name, then label, then id, then topic
                name = item.get("name") or item.get("label") or item.get("id") or item.get("topic")
                if name and not _is_ignored(name) and not _is_ignored(item.get("id")):
                    devices[str(name)] = dict(item)
            elif item is not None and not _is_ignored(str(item)):
                devices[str(item)] = {"name": str(item), "state": item}
                
    elif isinstance(source, dict):
        _LOGGER.debug("Processing dict source with %d keys", len(source))
        for key, value in source.items():
            if _is_ignored(key):
                continue
            if isinstance(value, dict):
                if _is_ignored(value.get("id")) or _is_ignored(value.get("name")):
                    continue
                device = dict(value)
                # Force the use of 'name' or 'label' if it exists inside the dict, otherwise use the key
                preferred_name = device.get("name") or device.get("label") or key
                device["name"] = preferred_name
                devices[str(key)] = device
            elif key not in {
                "type", "aqualinkd_version", "date", "time", "temp_units", "status", 
                "panel_message", "panel_type", "panel_type_full", "version", "battery", 
                "swg_fullstatus", "swg_percent", "swg_ppm", "pool_temp", "spa_temp", 
                "air_temp", "pool_htr_set_pnt", "spa_htr_set_pnt", "frz_protect_set_pnt",
                "leds", "timers", "timer_durations", "sensors", "light_program_names", "alternate_modes"
            }:
                # Avoid adding global metadata or known redundant status fields as new devices
                devices[str(key)] = {"name": key, "state": value}

    _LOGGER.debug("Flattened into %d devices: %s", len(devices), list(devices.keys()))
    return devices


def find_first_key(d: dict[str, Any], keys: tuple[str, ...]) -> Any:
    lower = {str(k).lower(): k for k in d.keys()}
    for wanted in keys:
        key = lower.get(wanted.lower())
        if key is not None:
            return d[key]
    return None
