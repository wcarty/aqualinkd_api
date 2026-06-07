from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AqualinkDApiClient
from .const import (
    CONF_CREATE_RAW_SENSORS,
    CONF_FILTER_PUMP_ZEROS,
    CONF_HOST,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    CONF_SCHEME,
    CONF_STALE_TIMEOUT,
    CONF_VERIFY_SSL,
    CONF_ZERO_GRACE_PERIOD,
    DEFAULT_CREATE_RAW_SENSORS,
    DEFAULT_FILTER_PUMP_ZEROS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_STALE_TIMEOUT,
    DEFAULT_VERIFY_SSL,
    DEFAULT_ZERO_GRACE_PERIOD,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import AqualinkDDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Setting up AqualinkD API entry: %s", entry.data[CONF_HOST])
    session = async_get_clientsession(hass, verify_ssl=entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL))
    client = AqualinkDApiClient(
        session=session,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        scheme=entry.data[CONF_SCHEME],
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
    )
    poll = entry.options.get(
        CONF_POLL_INTERVAL, entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
    )
    coordinator = AqualinkDDataUpdateCoordinator(
        hass=hass,
        client=client,
        update_interval=timedelta(seconds=poll),
        filter_pump_zeros=
            entry.options.get(
                CONF_FILTER_PUMP_ZEROS,
                entry.data.get(CONF_FILTER_PUMP_ZEROS, DEFAULT_FILTER_PUMP_ZEROS),
            ),
        zero_grace_period=
            entry.options.get(
                CONF_ZERO_GRACE_PERIOD,
                entry.data.get(CONF_ZERO_GRACE_PERIOD, DEFAULT_ZERO_GRACE_PERIOD),
            ),
        stale_timeout=
            entry.options.get(
                CONF_STALE_TIMEOUT,
                entry.data.get(CONF_STALE_TIMEOUT, DEFAULT_STALE_TIMEOUT),
            ),
        create_raw_sensors=
            entry.options.get(
                CONF_CREATE_RAW_SENSORS,
                entry.data.get(CONF_CREATE_RAW_SENSORS, DEFAULT_CREATE_RAW_SENSORS),
            ),
    )
    _LOGGER.debug("Performing first refresh for AqualinkD coordinator")
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as exc:
        _LOGGER.warning("First refresh failed for AqualinkD, will retry in background: %s", exc)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    _LOGGER.debug("Forwarding setups for platforms: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform(p) for p in PLATFORMS]
    )

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    _LOGGER.info("Successfully set up AqualinkD API integration for %s", entry.data[CONF_HOST])
    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [Platform(p) for p in PLATFORMS])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
