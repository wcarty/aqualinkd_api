from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "host": coordinator.client.host,
        "base_url": coordinator.client.base_url,
        "last_update_success": coordinator.last_update_success,
        "raw": coordinator.data.raw if coordinator.data else None,
        "devices_count": len(coordinator.data.devices) if coordinator.data else 0,
        "devices": list(coordinator.data.devices.keys()) if coordinator.data else [],
        "pump_filtered": coordinator.data.pump_filtered if coordinator.data else {},
    }
