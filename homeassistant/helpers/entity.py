"""Stub for homeassistant.helpers.entity used in the integration."""
from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceInfo:
    identifiers: Any = None
    name: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    configuration_url: str | None = None
