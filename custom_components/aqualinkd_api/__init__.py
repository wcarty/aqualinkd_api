"""AqualinkD API integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AqualinkDApiClient
from .const import (
    CONF_HOST,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    CONF_SCHEME,
    CONF_VERIFY_SSL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_VERIFY_SSL,
    PLATFORMS,
)
from .const import (
    DOMAIN as DOMAIN,
)
from .coordinator import AqualinkDDataUpdateCoordinator

AqualinkDConfigEntry = ConfigEntry[AqualinkDDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AqualinkDConfigEntry) -> bool:
    """Set up AqualinkD from a config entry."""
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
    client = AqualinkDApiClient(
        async_get_clientsession(hass, verify_ssl=verify_ssl),
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_SCHEME],
        verify_ssl=verify_ssl,
    )
    coordinator = AqualinkDDataUpdateCoordinator(
        hass,
        client,
        timedelta(
            seconds=entry.options.get(
                CONF_POLL_INTERVAL,
                entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
            )
        ),
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: AqualinkDConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: AqualinkDConfigEntry) -> bool:
    """Unload an AqualinkD config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
