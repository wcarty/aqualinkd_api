from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AqualinkDEntity
from .util import as_float

_LOGGER = logging.getLogger(__name__)

STATE_KEYS = ("state", "status", "enabled", "on", "value")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    _LOGGER.debug("Starting climate platform setup for AqualinkD")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ClimateEntity] = []

    for name, dev in coordinator.data.devices.items():
        dev_type = str(dev.get("type", "")).lower()
        if dev_type == "setpoint_thermo" or "heater" in name.lower():
            _LOGGER.debug("Adding climate entity for %s", name)
            entities.append(AqualinkDClimate(coordinator, name))

    _LOGGER.debug("Climate platform setup complete, added %d entities", len(entities))
    async_add_entities(entities)

class AqualinkDClimate(AqualinkDEntity, ClimateEntity):
    _attr_precision = 1.0
    _attr_target_temperature_step = 1.0
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator, device_name: str) -> None:
        super().__init__(coordinator, device_name, "climate")
        self._attr_name = device_name
        self._attr_min_temp = 40
        self._attr_max_temp = 104

    @property
    def current_temperature(self) -> float | None:
        dev = self.coordinator.data.devices.get(self.device_name, {})
        val = as_float(dev.get("value"))
        # AqualinkD uses -999 for unknown/disconnected (common when Spa is off)
        if val is None or val <= -999.0:
            return 0.0
        return val

    @property
    def target_temperature(self) -> float | None:
        dev = self.coordinator.data.devices.get(self.device_name, {})
        return as_float(dev.get("spvalue"))

    @property
    def hvac_mode(self) -> HVACMode:
        dev = self.coordinator.data.devices.get(self.device_name, {})
        state = dev.get("state", "off").lower()
        if state == "on":
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        # We don't necessarily know if it's actually firing vs just enabled
        # but in most pool systems "On" means it will heat if below setpoint.
        return HVACAction.HEATING

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        dev_data = self.coordinator.data.devices.get(self.device_name, {})
        device_id = dev_data.get("id", self.device_name)

        # API v2.0: PUT /api/Pool_Heater/set with value=1
        state = 1 if hvac_mode == HVACMode.HEAT else 0
        await self.coordinator.client.set_device(device_id, state)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        dev_data = self.coordinator.data.devices.get(self.device_name, {})
        device_id = dev_data.get("id", self.device_name)

        # API v2.0: PUT /api/Pool_Heater/setpoint/set with value=85
        await self.coordinator.client.set_attribute(device_id, "setpoint", temp)
        await self.coordinator.async_request_refresh()
