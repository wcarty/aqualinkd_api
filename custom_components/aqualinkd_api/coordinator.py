from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AqualinkDApiClient
from .util import as_bool, as_float, find_first_key, flatten_devices, slugify

_LOGGER = logging.getLogger(__name__)

PUMP_HINTS = ("pump", "filter")
RPM_KEYS = ("rpm", "RPM", "Pump_RPM", "speed", "Speed")
WATT_KEYS = ("watts", "Watts", "Pump_Watts", "watt", "Watt", "power", "Power")
GPM_KEYS = ("gpm", "GPM", "Pump_GPM", "flow", "Flow")
STATE_KEYS = ("state", "status", "enabled", "on", "value")

@dataclass
class PumpCache:
    last_valid_rpm: float | None = None
    last_valid_watts: float | None = None
    last_valid_time: datetime | None = None
    filter_state: str = "unknown"
    stale: bool = False

@dataclass
class ProcessedData:
    raw: dict[str, Any]
    devices: dict[str, dict[str, Any]]
    pump_filtered: dict[str, dict[str, Any]] = field(default_factory=dict)

class AqualinkDDataUpdateCoordinator(DataUpdateCoordinator[ProcessedData]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: AqualinkDApiClient,
        update_interval: timedelta,
        filter_pump_zeros: bool,
        zero_grace_period: int,
        stale_timeout: int,
        create_raw_sensors: bool,
    ) -> None:
        super().__init__(hass, _LOGGER, name="AqualinkD API", update_interval=update_interval)
        self.client = client
        self.filter_pump_zeros = filter_pump_zeros
        self.zero_grace_period = timedelta(seconds=zero_grace_period)
        self.stale_timeout = timedelta(seconds=stale_timeout)
        self.create_raw_sensors = create_raw_sensors
        self._pump_cache: dict[str, PumpCache] = {}

    async def _async_update_data(self) -> ProcessedData:
        try:
            # Fetch from all potential endpoints in parallel to maximize discovery.
            results = await asyncio.gather(
                self._safe_fetch(self.client.get_devices, "devices"),
                self._safe_fetch(self.client.get_status, "status"),
                self._safe_fetch(self.client.get_status_json, "status_json"),
                self._safe_fetch(self.client.get_config_json, "config_json"),
                return_exceptions=False,
            )
            
            devices_raw = results[0]
            status_raw = results[1]
            status_json_raw = results[2]
            config_json_raw = results[3]

            # Flatten and merge all sources with high precision.
            # We track devices by both ID and Name to ensure perfect alignment.
            id_map: dict[str, dict[str, Any]] = {}
            name_map: dict[str, dict[str, Any]] = {}
            
            for source_data in [devices_raw, status_raw, status_json_raw, config_json_raw]:
                flat_source = flatten_devices(source_data)
                for name, dev_data in flat_source.items():
                    dev_id = dev_data.get("id")
                    
                    # 1. Try to match by ID
                    target = None
                    if dev_id and dev_id in id_map:
                        target = id_map[dev_id]
                    # 2. Try to match if the explicit ID was previously used as a Name
                    elif dev_id and dev_id in name_map:
                        target = name_map[dev_id]
                    # 3. Try to match if the incoming Name is actually a known ID
                    elif name in id_map:
                        target = id_map[name]
                    # 4. Try to match by Name
                    elif name in name_map:
                        target = name_map[name]
                    # 5. Try to match by slugified name
                    else:
                        name_slug = slugify(name)
                        for existing_name, existing_data in name_map.items():
                            if slugify(existing_name) == name_slug:
                                target = existing_data
                                break
                    
                    if target:
                        # PROTECT ACTIVE STATES: Do not let stale "off" data overwrite a known "on" state
                        existing_state = str(target.get("state", "")).lower()
                        new_state = str(dev_data.get("state", "")).lower()
                        
                        target.update(dev_data)
                        
                        if (
                            existing_state
                            in ("on", "1", "enabled", "true")
                            and new_state in ("off", "0", "disabled", "false")
                        ):
                            target["state"] = existing_state
                            
                        # Keep the "prettiest" name
                        current_name = target.get("name", name)
                        if " " in name and " " not in current_name:
                            target["name"] = name
                            
                        # Track the new ID if it was previously unknown
                        if dev_id:
                            id_map[dev_id] = target
                    else:
                        # New entry
                        entry = dict(dev_data)
                        entry.setdefault("name", name)
                        name_map[name] = entry
                        if dev_id:
                            id_map[dev_id] = entry
            
            # The final devices list is the set of unique entries we've built
            unique_entries = []
            seen_ids = set()
            for entry in name_map.values():
                entry_ptr = id(entry)
                if entry_ptr not in seen_ids:
                    unique_entries.append(entry)
                    seen_ids.add(entry_ptr)
            
            devices = {data["name"]: data for data in unique_entries}
            
            _LOGGER.debug("Merged into %d unique devices: %s", len(devices), list(devices.keys()))

            pump_filtered = self._process_pumps(devices)
            _LOGGER.debug("Pump filtered data: %s", pump_filtered)

            return ProcessedData(
                raw={
                    "devices": devices_raw,
                    "status": status_raw,
                    "status_json": status_json_raw,
                    "config_json": config_json_raw
                },
                devices=devices,
                pump_filtered=pump_filtered
            )
        except Exception as exc:
            _LOGGER.error("Unexpected error during data update: %s", exc)
            raise UpdateFailed(f"Unexpected error: {exc}") from exc

    async def _safe_fetch(self, func, label: str) -> Any:
        try:
            return await func()
        except Exception as exc:
            _LOGGER.debug("Could not fetch %s: %s", label, exc)
            return {}

    def _process_pumps(self, devices: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        now = datetime.now(timezone.utc)
        result: dict[str, dict[str, Any]] = {}
        for name, dev in devices.items():
            lname = name.lower()
            
            # Identify if this is a pump
            is_pump = any(h in lname for h in PUMP_HINTS)
            
            # Check if it's an ePump / VSP (Variable Speed Pump)
            # These are the ones with telemetry (RPM, Watts, etc.)
            pump_type = str(dev.get("Pump_Type", dev.get("type_ext", ""))).lower()
            is_epump = "epump" in pump_type or "vsp" in pump_type
            
            if not (is_pump and is_epump):
                _LOGGER.debug(
                    "Skipping telemetry for %s: is_pump=%s is_epump=%s type=%s",
                    name,
                    is_pump,
                    is_epump,
                    pump_type,
                )
                continue
                
            raw_rpm = as_float(find_first_key(dev, RPM_KEYS))
            raw_watts = as_float(find_first_key(dev, WATT_KEYS))
            raw_gpm = as_float(find_first_key(dev, GPM_KEYS))
            state_value = find_first_key(dev, STATE_KEYS)
            pump_on = as_bool(state_value)
            if pump_on is None:
                pump_on = bool((raw_rpm or 0) > 0 or (raw_watts or 0) > 0)

            cache = self._pump_cache.setdefault(name, PumpCache())
            (
                filtered_rpm,
                filtered_watts,
                filtered_gpm,
                filter_state,
                stale,
            ) = self._filter_pump(
                name,
                pump_on,
                raw_rpm,
                raw_watts,
                raw_gpm,
                now,
                cache,
            )
            result[name] = {
                "raw_rpm": raw_rpm,
                "raw_watts": raw_watts,
                "raw_gpm": raw_gpm,
                "rpm": filtered_rpm,
                "watts": filtered_watts,
                "gpm": filtered_gpm,
                "pump_on": pump_on,
                "filter_state": filter_state,
                "stale": stale,
            }
        return result

    def _filter_pump(
        self,
        name: str,
        pump_on: bool,
        raw_rpm: float | None,
        raw_watts: float | None,
        raw_gpm: float | None,
        now: datetime,
        cache: PumpCache,
    ) -> tuple[float | None, float | None, float | None, str, bool]:
        if not self.filter_pump_zeros:
            return raw_rpm, raw_watts, raw_gpm, "raw", False

        # If pump is OFF, always return 0, regardless of raw telemetry
        if not pump_on:
            cache.last_valid_rpm = 0
            cache.last_valid_watts = 0
            cache.last_valid_time = now
            return 0, 0, 0, "pump_off", False

        raw_valid = raw_rpm is not None or raw_watts is not None
        rpm = raw_rpm or 0
        watts = raw_watts or 0
        raw_zero = rpm == 0 and watts == 0

        if not raw_valid:
            if cache.last_valid_time and now - cache.last_valid_time < self.stale_timeout:
                return cache.last_valid_rpm, cache.last_valid_watts, 0, "held_last_valid", False
            return None, None, None, "unavailable", True

        if pump_on and not raw_zero:
            cache.last_valid_rpm = raw_rpm
            cache.last_valid_watts = raw_watts
            cache.last_valid_time = now
            return raw_rpm, raw_watts, raw_gpm, "valid", False

        if pump_on and raw_zero:
            if cache.last_valid_time and now - cache.last_valid_time < self.stale_timeout:
                # If pump is on but reports 0, hold last valid if within timeout
                return cache.last_valid_rpm, cache.last_valid_watts, 0, "suppressed_zero", False
            return None, None, None, "stale", True

        return raw_rpm, raw_watts, raw_gpm, "raw", False
