from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AqualinkDEntity
from .util import as_bool, find_first_key

_LOGGER = logging.getLogger(__name__)

STATE_KEYS = ("state", "status", "enabled", "on", "value")
CONTROL_HINTS = ("pump", "spa", "light", "aux", "blower", "booster", "clean", "mode", "heater", "spill", "solar")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    _LOGGER.debug("Starting switch platform setup for AqualinkD")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SwitchEntity] = []
    _LOGGER.debug("Setting up switches for %d devices", len(coordinator.data.devices))
    for name, dev in coordinator.data.devices.items():
        lname = name.lower()
        dev_type = str(dev.get("type", "")).lower()
        
        # Explicitly exclude types that shouldn't be switches or are handled by climate
        if any(t in dev_type for t in ("temp", "sensor", "value", "ppm", "ph", "orp", "setpoint_thermo")):
            _LOGGER.debug("Skipping switch for %s due to type %s", name, dev_type)
            continue
            
        if "heater" in lname:
            _LOGGER.debug("Skipping switch for %s (handled by climate)", name)
            continue
            
        state_val = find_first_key(dev, STATE_KEYS)
        state = as_bool(state_val)
        _LOGGER.debug("Checking device %s for switch compatibility. Type: %s, State: %s", name, dev_type, state)
        
        # If it's explicitly a switch type, or a heater, or matches our hints, or has a boolean state
        is_switchable = (
            dev_type in {"switch", "setpoint_thermo", "setpoint_swg"} or 
            any(h in lname for h in CONTROL_HINTS) or 
            state is not None
        )
        
        if is_switchable:
            _LOGGER.debug("Adding switch entity for %s", name)
            entities.append(AqualinkDSwitch(coordinator, name))
    _LOGGER.debug("Switch platform setup complete, added %d entities", len(entities))
    async_add_entities(entities)

class AqualinkDSwitch(AqualinkDEntity, SwitchEntity):
    def __init__(self, coordinator, device_name: str) -> None:
        super().__init__(coordinator, device_name, "switch")
        self._attr_name = device_name

    @property
    def is_on(self) -> bool | None:
        dev = self.coordinator.data.devices.get(self.device_name, {})
        return as_bool(find_first_key(dev, STATE_KEYS))

    async def async_turn_on(self, **kwargs) -> None:
        dev_data = self.coordinator.data.devices.get(self.device_name, {})
        device_id = dev_data.get("id", self.device_name)
        await self.coordinator.client.set_device(device_id, 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        dev_data = self.coordinator.data.devices.get(self.device_name, {})
        device_id = dev_data.get("id", self.device_name)
        await self.coordinator.client.set_device(device_id, 0)
        await self.coordinator.async_request_refresh()
