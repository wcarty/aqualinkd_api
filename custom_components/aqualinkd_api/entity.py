from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import AqualinkDDataUpdateCoordinator
from .util import slugify

class AqualinkDEntity(CoordinatorEntity[AqualinkDDataUpdateCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AqualinkDDataUpdateCoordinator, device_name: str, attr: str) -> None:
        super().__init__(coordinator)
        self.device_name = device_name
        self.attr = attr
        
        # Extract platform name from class (e.g., AqualinkDClimate -> climate)
        cls_name = self.__class__.__name__.lower()
        if "climate" in cls_name:
            platform = "climate"
        elif "switch" in cls_name:
            platform = "switch"
        elif "number" in cls_name:
            platform = "number"
        elif "binary" in cls_name:
            platform = "binary_sensor"
        else:
            platform = "sensor"

        host_slug = slugify(coordinator.client.host)
        dev_slug = slugify(device_name)
        attr_slug = slugify(attr)
        
        # Standardize the unique ID to ensure HA generates the 'aqualinkd_api' slug
        self._attr_unique_id = f"aqualinkd_api_{host_slug}_{dev_slug}_{platform}_{attr_slug}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.client.host)},
            name="AqualinkD API",
            manufacturer="AqualinkD",
            model="AqualinkD API",
            configuration_url=self.coordinator.client.base_url,
        )
