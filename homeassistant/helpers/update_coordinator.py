"""Stub for homeassistant.helpers.update_coordinator used in the integration."""
from typing import Generic, TypeVar

T = TypeVar("T")


class UpdateFailed(Exception):
    pass


class DataUpdateCoordinator(Generic[T]):
    def __init__(self, hass, logger, name: str | None = None, update_interval=None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval


class CoordinatorEntity(Generic[T]):
    def __init__(self, coordinator: DataUpdateCoordinator[T]):
        self.coordinator = coordinator
