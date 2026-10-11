"""Sensor entities for AqualinkD."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AqualinkDConfigEntry
from .entity import AqualinkDEntity
from .util import pump_status_records


def _number(value: Any) -> float | None:
    """Convert an AqualinkD numeric string to a usable value."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if number <= -999 else number


@dataclass(frozen=True, kw_only=True)
class AqualinkDSensorDescription(SensorEntityDescription):
    """Describe a status sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


STATUS_DESCRIPTIONS = (
    AqualinkDSensorDescription(
        key="controller_status",
        translation_key="controller_status",
        value_fn=lambda status: status.get("status"),
    ),
    AqualinkDSensorDescription(
        key="panel_age",
        translation_key="panel_age",
        native_unit_of_measurement="s",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda status: _number(status.get("panel_age_seconds")),
    ),
    AqualinkDSensorDescription(
        key="chemistry_age",
        translation_key="chemistry_age",
        native_unit_of_measurement="s",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda status: _number(status.get("chem_age_seconds")),
    ),
    AqualinkDSensorDescription(
        key="swg_age",
        translation_key="swg_age",
        native_unit_of_measurement="s",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda status: _number(status.get("swg_age_seconds")),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AqualinkDConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AqualinkD sensors."""
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        AqualinkDStatusSensor(coordinator, description) for description in STATUS_DESCRIPTIONS
    ]
    entities.extend(
        AqualinkDPumpAgeSensor(coordinator, device_id) for device_id in pump_status_records(coordinator.data.status)
    )

    for device_id, device in coordinator.data.devices.items():
        device_type = str(device.get("type", "")).lower()
        if device_type in {"temperature", "value"}:
            entities.append(AqualinkDValueSensor(coordinator, device_id, "value"))

        if device_type == "setpoint_thermo":
            entities.extend(
                (
                    AqualinkDValueSensor(coordinator, device_id, "value", "current_temperature"),
                    AqualinkDValueSensor(coordinator, device_id, "spvalue", "target_temperature"),
                )
            )

        if "Pump_RPM" in device:
            entities.extend(
                (
                    AqualinkDValueSensor(coordinator, device_id, "Pump_RPM"),
                    AqualinkDValueSensor(coordinator, device_id, "Pump_Watts"),
                    AqualinkDValueSensor(coordinator, device_id, "Pump_GPM"),
                )
            )

    async_add_entities(entities)


class AqualinkDStatusSensor(AqualinkDEntity, SensorEntity):
    """Represent controller-level status."""

    entity_description: AqualinkDSensorDescription

    def __init__(self, coordinator, description: AqualinkDSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the current status value."""
        return self.entity_description.value_fn(self.coordinator.data.status)


class AqualinkDPumpAgeSensor(AqualinkDEntity, SensorEntity):
    """Represent the acquisition age for one pump."""

    _attr_native_unit_of_measurement = "s"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, f"{device_id}_age")
        self._device_id = device_id
        pump = pump_status_records(coordinator.data.status)[device_id]
        pump_name = pump.get("name") or coordinator.data.devices.get(device_id, {}).get("name", device_id)
        self._attr_name = f"{pump_name} Data Age"

    @property
    def native_value(self) -> float | None:
        """Return seconds since the pump was last acquired."""
        pump = pump_status_records(self.coordinator.data.status).get(self._device_id, {})
        return _number(pump.get("age_seconds"))


class AqualinkDValueSensor(AqualinkDEntity, SensorEntity):
    """Represent one read-only device value."""

    def __init__(
        self,
        coordinator,
        device_id: str,
        attribute: str,
        name_suffix: str | None = None,
    ) -> None:
        super().__init__(coordinator, f"{device_id}_{attribute}")
        self._device_id = device_id
        self._attribute = attribute
        device = coordinator.data.devices[device_id]
        device_name = device.get("name", device_id)
        suffix = name_suffix or attribute
        self._attr_name = (
            device_name
            if attribute == "value" and name_suffix is None
            else f"{device_name} {suffix.replace('_', ' ').title()}"
        )
        self._configure_measurement(device)

    def _configure_measurement(self, device: dict[str, Any]) -> None:
        device_id = self._device_id.lower()
        attribute = self._attribute.lower()
        device_type = str(device.get("type", "")).lower()
        uom = str(device.get("uom", ""))

        if device_type == "temperature" or "temperature" in device_id:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            units = self.coordinator.data.status.get("temp_units", "f").lower()
            self._attr_native_unit_of_measurement = (
                UnitOfTemperature.CELSIUS if units == "c" else UnitOfTemperature.FAHRENHEIT
            )
        elif "watts" in attribute:
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = UnitOfPower.WATT
        elif "rpm" in attribute:
            self._attr_native_unit_of_measurement = "RPM"
        elif "gpm" in attribute:
            self._attr_native_unit_of_measurement = "gal/min"
        elif "orp" in device_id:
            self._attr_native_unit_of_measurement = "mV"
        elif "ppm" in device_id:
            self._attr_native_unit_of_measurement = "ppm"
        elif "percent" in device_id or uom == "%":
            self._attr_native_unit_of_measurement = PERCENTAGE

        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | str | None:
        """Return the latest value."""
        value = self.coordinator.data.devices.get(self._device_id, {}).get(self._attribute)
        return _number(value)
