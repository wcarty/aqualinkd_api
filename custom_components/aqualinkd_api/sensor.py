from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AqualinkDEntity
from .util import as_float

_LOGGER = logging.getLogger(__name__)

TEMP_KEYS = ("temp", "temperature")
SALT_KEYS = ("salt", "salinity", "ppm")
PH_KEYS = ("ph", "pH")
ORP_KEYS = ("orp", "ORP")
PERCENT_KEYS = ("percent", "percentage", "%")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    _LOGGER.debug("Starting sensor platform setup for AqualinkD")
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    # Keep track of (device, attribute) pairs we've already created sensors for
    handled_attrs: set[tuple[str, str]] = set()

    # Add pump sensors first
    _add_pump_sensors(coordinator, entities, handled_attrs)

    # Add device sensors
    _add_device_sensors(coordinator, entities, handled_attrs)

    _LOGGER.debug("Sensor platform setup complete, added %d entities", len(entities))
    async_add_entities(entities)


def _add_pump_sensors(coordinator, entities: list[SensorEntity], handled_attrs: set[tuple[str, str]]) -> None:
    for pump_name in coordinator.data.pump_filtered:
        _LOGGER.debug("Adding pump sensors for %s", pump_name)
        entities.extend(
            [
                PumpFilteredSensor(coordinator, pump_name, "rpm", "RPM"),
                PumpFilteredSensor(coordinator, pump_name, "watts", "Watts"),
                PumpFilteredSensor(
                    coordinator, pump_name, "filter_state", "Telemetry Filter State"
                ),
            ]
        )

        # Mark these as handled so the generic loop doesn't create duplicates
        handled_attrs.update(
            {
                (pump_name, "rpm"),
                (pump_name, "watts"),
                (pump_name, "filter_state"),
                (pump_name, "Pump_RPM"),
                (pump_name, "Pump_Watts"),
                (pump_name, "Pump_GPM"),
                (pump_name, "raw_rpm"),
                (pump_name, "raw_watts"),
                (pump_name, "raw_gpm"),
            }
        )


def _add_device_sensors(coordinator, entities: list[SensorEntity], handled_attrs: set[tuple[str, str]]) -> None:
    for name, dev in coordinator.data.devices.items():
        name_l = name.lower()
        dev_type = str(dev.get("type", "")).lower()
        _LOGGER.debug("Processing device %s (type: %s) for sensors", name, dev_type)

        # If this device has both 'state' and 'value', 'state' is usually just 'on/off'
        # while 'value' is the actual data. We should skip 'state' to avoid errors.
        has_real_value = "value" in dev or "spvalue" in dev or "Pump_RPM" in dev

        for key, val in dev.items():
            if key in {"name", "id", "type", "type_ext", "int_status", "timer_active"} or isinstance(
                val, (dict, list)
            ):
                continue

            if (name, key) in handled_attrs:
                continue

            if has_real_value and key in {"state", "status", "int_status"}:
                _LOGGER.debug(
                    "Skipping generic state key %s for %s as it has a real value attribute",
                    key,
                    name,
                )
                continue

            key_l = str(key).lower()
            is_generic_key = key_l in {"state", "value", "status"}
            is_numeric = isinstance(val, (int, float)) or as_float(val) is not None

            # Identify if this specific (device, key) is a sensor we want
            is_sensor = False

            # Skip if it's a heater temperature (handled by climate)
            if "heater" in name_l:
                _LOGGER.debug(
                    "Skipping heater sensor for %s attribute %s (handled by climate)", name, key
                )
                continue

            # Skip redundant Aux display/status sensors (handled by switch)
            if "aux" in name_l or "aux" in key_l:
                _LOGGER.debug("Skipping redundant Aux sensor for %s attribute %s", name, key)
                continue

            # Skip any attribute specifically named 'display'
            if "display" in key_l:
                _LOGGER.debug("Skipping 'display' sensor for %s attribute %s", name, key)
                continue

            # 1. Explicit temperature/sensor types from API
            if any(
                t in dev_type for t in ("temperature", "sensor", "value", "ppm", "ph", "orp", "setpoint")
            ):
                if is_generic_key or is_numeric:
                    is_sensor = True

            # 2. Specialized keywords in key or name
            keys_to_check = TEMP_KEYS + SALT_KEYS + PH_KEYS + ORP_KEYS + PERCENT_KEYS
            if any(k.lower() in key_l for k in keys_to_check):
                is_sensor = True
            elif is_generic_key and any(k.lower() in name_l for k in keys_to_check):
                is_sensor = True

            # 3. Numeric attributes that aren't the main state
            if is_numeric and not is_generic_key:
                # Still skip if it's already handled (like Pump_RPM handled as 'rpm')
                if any(p in key_l for p in ("rpm", "watt", "gpm")):
                    if (name, "rpm") in handled_attrs or (name, "watts") in handled_attrs:
                        continue
                is_sensor = True

            # 4. Fallback for other descriptive keys, but be careful with generic ones
            if not is_sensor and not is_generic_key and len(key_l) > 3:
                is_sensor = True

            if is_sensor:
                _LOGGER.debug("Adding sensor for %s attribute %s", name, key)
                entities.append(GenericDeviceSensor(coordinator, name, str(key)))
                handled_attrs.add((name, key))

class PumpFilteredSensor(AqualinkDEntity, SensorEntity):
    def __init__(self, coordinator, device_name: str, attr: str, label: str) -> None:
        super().__init__(coordinator, device_name, attr)
        self._attr_name = f"{device_name} {label}"
        if "rpm" in attr:
            self._attr_native_unit_of_measurement = "RPM"
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif "watt" in attr:
            self._attr_native_unit_of_measurement = "W"
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif "gpm" in attr:
            self._attr_native_unit_of_measurement = "GPM"
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        pump = self.coordinator.data.pump_filtered.get(self.device_name, {})
        return pump.get(self.attr)

    @property
    def available(self) -> bool:
        if self.attr in {"rpm", "watts"}:
            return not self.coordinator.data.pump_filtered.get(self.device_name, {}).get("stale", False)
        return super().available

class GenericDeviceSensor(AqualinkDEntity, SensorEntity):
    def __init__(self, coordinator, device_name: str, attr: str) -> None:
        super().__init__(coordinator, device_name, attr)
        
        # Clean up the name
        clean_attr = attr.replace("_", " ").replace(device_name, "").strip()
        if attr.lower() in {"state", "value", "status"} or not clean_attr:
            self._attr_name = device_name
        else:
            self._attr_name = f"{device_name} {clean_attr}"
            
        key_l = attr.lower()
        name_l = device_name.lower()
        val = self.coordinator.data.devices.get(self.device_name, {}).get(self.attr)
        is_numeric = isinstance(val, (int, float)) or as_float(val) is not None

        # Only assign measurement properties if the value is actually numeric
        if is_numeric:
            if "temp" in key_l or "temp" in name_l:
                self._attr_device_class = SensorDeviceClass.TEMPERATURE
                self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif "watt" in key_l:
                self._attr_device_class = SensorDeviceClass.POWER
                self._attr_native_unit_of_measurement = "W"
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif "rpm" in key_l:
                self._attr_native_unit_of_measurement = "RPM"
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif "percent" in key_l or "%" in key_l or "percent" in name_l:
                self._attr_native_unit_of_measurement = PERCENTAGE
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif "orp" in key_l or "orp" in name_l:
                self._attr_native_unit_of_measurement = "mV"
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif "ph" in key_l or "ph" in name_l:
                self._attr_state_class = SensorStateClass.MEASUREMENT
            elif "salt" in key_l or "ppm" in key_l or "salt" in name_l or "ppm" in name_l:
                self._attr_native_unit_of_measurement = "ppm"
                self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        val = self.coordinator.data.devices.get(self.device_name, {}).get(self.attr)
        num = as_float(val)
        
        # Handle AqualinkD -999.0 for inactive sensors (common for Spa when off)
        if num is not None and num <= -999.0:
            return 0.0
            
        return num if num is not None else val
