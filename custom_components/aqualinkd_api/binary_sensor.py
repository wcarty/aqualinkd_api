from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AqualinkDEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []
    for pump_name in coordinator.data.pump_filtered:
        entities.append(PumpTelemetryStaleBinarySensor(coordinator, pump_name))
    async_add_entities(entities)

class PumpTelemetryStaleBinarySensor(AqualinkDEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, device_name: str) -> None:
        super().__init__(coordinator, device_name, "telemetry_stale")
        self._attr_name = f"{device_name} Telemetry Stale"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.pump_filtered.get(self.device_name, {}).get("stale", False))
