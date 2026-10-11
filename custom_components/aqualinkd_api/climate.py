"""Climate controls for AqualinkD heaters."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACAction, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AqualinkDConfigEntry
from .const import CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS
from .entity import AqualinkDEntity
from .util import as_bool, as_float


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AqualinkDConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up opt-in heater controls."""
    if not entry.options.get(
        CONF_ENABLE_CONTROLS,
        entry.data.get(CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS),
    ):
        return

    coordinator = entry.runtime_data
    async_add_entities(
        AqualinkDClimate(coordinator, device_id)
        for device_id, device in coordinator.data.devices.items()
        if device.get("type") == "setpoint_thermo"
    )


class AqualinkDClimate(AqualinkDEntity, ClimateEntity):
    """Control one pool or spa heater."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_target_temperature_step = 1

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, f"{device_id}_climate")
        self._device_id = device_id
        self._attr_name = coordinator.data.devices[device_id].get("name", device_id)
        units = coordinator.data.status.get("temp_units", "f").lower()
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS if units == "c" else UnitOfTemperature.FAHRENHEIT
        self._attr_min_temp = 4 if units == "c" else 40
        self._attr_max_temp = 40 if units == "c" else 104

    @property
    def current_temperature(self) -> float | None:
        """Return the current water temperature."""
        value = as_float(self.coordinator.data.devices.get(self._device_id, {}).get("value"))
        return None if value is None or value <= -999 else value

    @property
    def target_temperature(self) -> float | None:
        """Return the configured set point."""
        return as_float(self.coordinator.data.devices.get(self._device_id, {}).get("spvalue"))

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the heater mode."""
        device = self.coordinator.data.devices.get(self._device_id, {})
        return HVACMode.HEAT if as_bool(device.get("status")) else HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        """Return the reported heater action."""
        device = self.coordinator.data.devices.get(self._device_id, {})
        if as_bool(device.get("state")):
            return HVACAction.HEATING
        if self.hvac_mode is HVACMode.HEAT:
            return HVACAction.IDLE
        return HVACAction.OFF

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Enable or disable the heater."""
        await self.coordinator.client.set_device(self._device_id, hvac_mode is HVACMode.HEAT)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the heater target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self.coordinator.client.set_attribute(self._device_id, "setpoint", temperature)
        await self.coordinator.async_request_refresh()
