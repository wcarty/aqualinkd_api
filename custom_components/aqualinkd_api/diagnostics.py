"""Diagnostics support for AqualinkD API."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import AqualinkDConfigEntry


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: AqualinkDConfigEntry) -> dict[str, Any]:
    """Return non-sensitive integration diagnostics."""
    coordinator = entry.runtime_data
    return {
        "host": coordinator.client.host,
        "port": coordinator.client.port,
        "scheme": coordinator.client.scheme,
        "last_update_success": coordinator.last_update_success,
        "controller_status": coordinator.data.status,
        "device_ids": sorted(coordinator.data.devices),
    }
