"""Numeric controls for AqualinkD set points."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AqualinkDConfigEntry
from .const import CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS
from .entity import AqualinkDEntity
from .util import as_float


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AqualinkDConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up opt-in set point controls."""
    if not entry.options.get(
        CONF_ENABLE_CONTROLS,
        entry.data.get(CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS),
    ):
        return

    coordinator = entry.runtime_data
    entities: list[NumberEntity] = []
    for device_id, device in coordinator.data.devices.items():
        device_type = device.get("type")
        if device_type == "setpoint_swg":
            entities.append(
                AqualinkDSetpointNumber(
                    coordinator,
                    device_id,
                    "Percent",
                    0,
                    100,
                    1,
                    PERCENTAGE,
                )
            )
        elif device_type == "setpoint_freeze":
            units = coordinator.data.status.get("temp_units", "f").lower()
            entities.append(
                AqualinkDSetpointNumber(
                    coordinator,
                    device_id,
                    "setpoint",
                    1 if units == "c" else 34,
                    6 if units == "c" else 42,
                    1,
                    UnitOfTemperature.CELSIUS if units == "c" else UnitOfTemperature.FAHRENHEIT,
                )
            )
    async_add_entities(entities)


class AqualinkDSetpointNumber(AqualinkDEntity, NumberEntity):
    """Control an AqualinkD numeric set point."""

    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator,
        device_id: str,
        api_attribute: str,
        minimum: float,
        maximum: float,
        step: float,
        unit: str,
    ) -> None:
        super().__init__(coordinator, f"{device_id}_{api_attribute}_control")
        self._device_id = device_id
        self._api_attribute = api_attribute
        self._attr_name = f"{coordinator.data.devices[device_id].get('name', device_id)} Setpoint"
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        """Return the current set point."""
        return as_float(self.coordinator.data.devices.get(self._device_id, {}).get("spvalue"))

    async def async_set_native_value(self, value: float) -> None:
        """Set the target value."""
        await self.coordinator.client.set_attribute(self._device_id, self._api_attribute, value)
        await self.coordinator.async_request_refresh()
