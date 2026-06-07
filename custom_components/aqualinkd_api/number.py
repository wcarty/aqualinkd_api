from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AqualinkDEntity
from .util import as_float

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    _LOGGER.debug("Starting number platform setup for AqualinkD")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[NumberEntity] = []
    
    _LOGGER.debug("Setting up number entities for %d devices", len(coordinator.data.devices))
    for name, dev in coordinator.data.devices.items():
        lname = name.lower()
        dev_type = str(dev.get("type", "")).lower()
        
        # Only add number entities for devices that actually have controllable setpoints
        # Avoid creating sliders for simple switches or status values
        
        # 1. Salt Water Generator (SWG)
        if dev_type == "setpoint_swg" or ("swg" in lname and "boost" not in lname):
            # Only if it has a setpoint key or we are sure it's the main SWG
            if "spvalue" in dev or any("percent" in k.lower() for k in dev) or dev_type == "setpoint_swg":
                attr = "spvalue" if "spvalue" in dev else next((k for k in dev if "percent" in k.lower()), "Percent")
                _LOGGER.debug("Adding SWG slider for %s attribute %s", name, attr)
                entities.append(AqualinkDAttributeNumber(coordinator, name, attr, "Output", 0, 100, 1, PERCENTAGE))
        
        # 2. Heaters (Handled by climate platform, so we skip them here)
        elif "heater" in lname:
            _LOGGER.debug("Skipping heater number for %s (handled by climate)", name)
            continue
            
        # 3. Pumps (Variable Speed)
        elif "pump" in lname or "filter" in lname:
            # Check if it has a setpoint or explicit RPM control
            if "spvalue" in dev or "RPM" in dev or "rpm" in dev:
                attr = "spvalue" if "spvalue" in dev else "RPM"
                _LOGGER.debug("Adding pump RPM slider for %s", name)
                entities.append(AqualinkDAttributeNumber(coordinator, name, attr, "RPM Setpoint", 600, 3450, 25, "RPM"))

    _LOGGER.debug("Number platform setup complete, added %d entities", len(entities))
    async_add_entities(entities)

class AqualinkDAttributeNumber(AqualinkDEntity, NumberEntity):
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator,
        device_name: str,
        attr: str,
        label: str,
        min_value: float,
        max_value: float,
        step: float,
        unit: str,
    ) -> None:
        super().__init__(coordinator, device_name, attr)
        self._attr_name = f"{device_name} {label}"
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        dev = self.coordinator.data.devices.get(self.device_name, {})
        return as_float(dev.get(self.attr))

    async def async_set_native_value(self, value: float) -> None:
        dev_data = self.coordinator.data.devices.get(self.device_name, {})
        device_id = dev_data.get("id", self.device_name)
        dev_type = str(dev_data.get("type", "")).lower()
        
        # Map common attributes to AqualinkD v2.0 attribute names
        attr = self.attr
        lname = self.device_name.lower()
        
        if dev_type == "setpoint_swg" or "swg" in lname or "salt" in lname:
            attr = "Percent"
        elif "pump" in lname or "filter" in lname:
            attr = "RPM"
        
        # API v2.0: PUT /api/{device_id}/{attr}/set with value=X
        await self.coordinator.client.set_attribute(device_id, attr, value)
        await self.coordinator.async_request_refresh()
