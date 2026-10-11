"""Shared AqualinkD entity base classes."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AqualinkDDataUpdateCoordinator


class AqualinkDEntity(CoordinatorEntity[AqualinkDDataUpdateCoordinator]):
    """Base entity attached to one AqualinkD controller."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AqualinkDDataUpdateCoordinator,
        unique_suffix: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.client.host}:{coordinator.client.port}_{unique_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the controller device."""
        status = self.coordinator.data.status
        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{self.coordinator.client.host}:{self.coordinator.client.port}",
                )
            },
            name="AqualinkD",
            manufacturer="AqualinkD",
            model=status.get("panel_type_full", status.get("panel_type", "Controller")),
            sw_version=status.get("aqualinkd_version"),
            hw_version=status.get("version"),
            configuration_url=self.coordinator.client.base_url,
        )
