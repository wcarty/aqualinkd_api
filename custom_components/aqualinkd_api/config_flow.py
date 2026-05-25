from __future__ import annotations

from typing import Any
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import callback

from .api import AqualinkDApiClient, AqualinkDApiError
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
    DEFAULT_PORT,
    DEFAULT_SCHEME,
    DEFAULT_STALE_TIMEOUT,
    DEFAULT_VERIFY_SSL,
    DEFAULT_ZERO_GRACE_PERIOD,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

class AqualinkDOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        _LOGGER.debug("Entered AqualinkDOptionsFlow async_step_init with user_input: %s", user_input)
        try:
            if user_input is not None:
                return self.async_create_entry(title="", data=user_input)

            opts = self._config_entry.options
            data = self._config_entry.data
            
            _LOGGER.debug("Building schema with opts: %s and data: %s", opts, data)
            
            # Use absolute basic types to prevent frontend rendering 500 errors
            schema = vol.Schema({
                vol.Optional(
                    CONF_POLL_INTERVAL, 
                    default=int(opts.get(CONF_POLL_INTERVAL, data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)))
                ): int,
                vol.Optional(
                    CONF_STALE_TIMEOUT, 
                    default=int(opts.get(CONF_STALE_TIMEOUT, data.get(CONF_STALE_TIMEOUT, DEFAULT_STALE_TIMEOUT)))
                ): int,
                vol.Optional(
                    CONF_FILTER_PUMP_ZEROS, 
                    default=bool(opts.get(CONF_FILTER_PUMP_ZEROS, data.get(CONF_FILTER_PUMP_ZEROS, DEFAULT_FILTER_PUMP_ZEROS)))
                ): bool,
                vol.Optional(
                    CONF_ZERO_GRACE_PERIOD, 
                    default=int(opts.get(CONF_ZERO_GRACE_PERIOD, data.get(CONF_ZERO_GRACE_PERIOD, DEFAULT_ZERO_GRACE_PERIOD)))
                ): int,
                vol.Optional(
                    CONF_CREATE_RAW_SENSORS, 
                    default=bool(opts.get(CONF_CREATE_RAW_SENSORS, data.get(CONF_CREATE_RAW_SENSORS, DEFAULT_CREATE_RAW_SENSORS)))
                ): bool,
            })
            
            _LOGGER.debug("Showing form with schema: %s", schema)
            return self.async_show_form(step_id="init", data_schema=schema)
            
        except Exception as exc:
            _LOGGER.exception("CRITICAL ERROR IN OPTIONS FLOW: %s", exc)
            # Re-raise so HA still knows it failed, but we get the log!
            raise

class AqualinkDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> AqualinkDOptionsFlow:
        """Create the options flow."""
        return AqualinkDOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_SCHEME]}://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
            self._abort_if_unique_id_configured()
            session = async_get_clientsession(self.hass, verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL))
            client = AqualinkDApiClient(session, user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_SCHEME], verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL))
            try:
                await client.get_devices()
            except AqualinkDApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=f"AqualinkD API {user_input[CONF_HOST]}", data=user_input)
        
        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_SCHEME, default=DEFAULT_SCHEME): vol.In(["http", "https"]),
            vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): vol.All(int, vol.Range(min=2, max=300)),
            vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
            vol.Optional(CONF_FILTER_PUMP_ZEROS, default=DEFAULT_FILTER_PUMP_ZEROS): bool,
            vol.Optional(CONF_ZERO_GRACE_PERIOD, default=DEFAULT_ZERO_GRACE_PERIOD): vol.All(int, vol.Range(min=5, max=600)),
            vol.Optional(CONF_STALE_TIMEOUT, default=DEFAULT_STALE_TIMEOUT): vol.All(int, vol.Range(min=30, max=1800)),
            vol.Optional(CONF_CREATE_RAW_SENSORS, default=DEFAULT_CREATE_RAW_SENSORS): bool,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
