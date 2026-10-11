"""Binary sensors for AqualinkD equipment status."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AqualinkDConfigEntry
from .entity import AqualinkDEntity
from .util import as_bool


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AqualinkDConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up read-only equipment status entities."""
    coordinator = entry.runtime_data
    entities: list[BinarySensorEntity] = [AqualinkDControllerReadyBinarySensor(coordinator)]

    for device_id, device in coordinator.data.devices.items():
        if device.get("type") in {
            "switch",
            "setpoint_swg",
            "setpoint_thermo",
        }:
            entities.append(AqualinkDEquipmentBinarySensor(coordinator, device_id))

    async_add_entities(entities)


class AqualinkDControllerReadyBinarySensor(AqualinkDEntity, BinarySensorEntity):
    """Report whether the daemon says it is ready."""

    _attr_name = "Controller Ready"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "controller_ready")

    @property
    def is_on(self) -> bool:
        """Return true when AqualinkD is ready."""
        return self.coordinator.data.status.get("status") == "Ready"


class AqualinkDEquipmentBinarySensor(AqualinkDEntity, BinarySensorEntity):
    """Represent read-only equipment state."""

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, f"{device_id}_status")
        self._device_id = device_id
        self._attr_name = f"{coordinator.data.devices[device_id].get('name', device_id)} Status"

    @property
    def is_on(self) -> bool | None:
        """Return the reported equipment state."""
        device = self.coordinator.data.devices.get(self._device_id, {})
        return as_bool(device.get("state", device.get("status")))
