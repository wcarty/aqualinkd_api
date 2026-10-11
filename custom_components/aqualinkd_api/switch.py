"""Switch controls for AqualinkD equipment."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AqualinkDConfigEntry
from .const import CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS
from .entity import AqualinkDEntity
from .util import as_bool


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AqualinkDConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up opt-in equipment controls."""
    if not entry.options.get(
        CONF_ENABLE_CONTROLS,
        entry.data.get(CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS),
    ):
        return

    coordinator = entry.runtime_data
    async_add_entities(
        AqualinkDSwitch(coordinator, device_id)
        for device_id, device in coordinator.data.devices.items()
        if device.get("type") == "switch"
    )


class AqualinkDSwitch(AqualinkDEntity, SwitchEntity):
    """Control an AqualinkD switch."""

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, f"{device_id}_control")
        self._device_id = device_id
        device_name = coordinator.data.devices[device_id].get("name", device_id)
        self._attr_name = device_name
        if any(keyword in device_name.lower() for keyword in ("acid", "chemical", "chlorine", "dose", "dosing")):
            self._attr_entity_registry_enabled_default = False

    @property
    def is_on(self) -> bool | None:
        """Return the reported state."""
        device = self.coordinator.data.devices.get(self._device_id, {})
        return as_bool(device.get("state", device.get("status")))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the equipment on."""
        await self.coordinator.client.set_device(self._device_id, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the equipment off."""
        await self.coordinator.client.set_device(self._device_id, False)
        await self.coordinator.async_request_refresh()
