"""Stub constants for Home Assistant used in tests."""

class UnitOfTemperature:
    FAHRENHEIT = "F"


PERCENTAGE = "%"


class Platform:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"Platform({self.name!r})"
