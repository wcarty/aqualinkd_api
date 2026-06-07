"""Stub for homeassistant.components.sensor used by the integration."""

class SensorEntity:
    def __init__(self, *args, **kwargs):
        pass


class SensorDeviceClass:
    TEMPERATURE = "temperature"
    POWER = "power"


class SensorStateClass:
    MEASUREMENT = "measurement"
