"""Config flow for AqualinkD API."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AqualinkDApiClient, AqualinkDApiError
from .const import (
    CONF_ENABLE_CONTROLS,
    CONF_HOST,
    CONF_POLL_INTERVAL,
    CONF_PORT,
    CONF_SCHEME,
    CONF_VERIFY_SSL,
    DEFAULT_ENABLE_CONTROLS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCHEME,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    MAX_POLL_INTERVAL,
    MIN_POLL_INTERVAL,
)


def _user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=values.get(CONF_HOST)): str,
            vol.Optional(CONF_PORT, default=values.get(CONF_PORT, DEFAULT_PORT)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
            vol.Optional(CONF_SCHEME, default=values.get(CONF_SCHEME, DEFAULT_SCHEME)): vol.In(("http", "https")),
            vol.Optional(
                CONF_POLL_INTERVAL,
                default=values.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL),
            ),
            vol.Optional(
                CONF_VERIFY_SSL,
                default=values.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            ): bool,
            vol.Optional(
                CONF_ENABLE_CONTROLS,
                default=values.get(CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS),
            ): bool,
        }
    )


class AqualinkDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle AqualinkD configuration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Configure an AqualinkD controller."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            user_input[CONF_HOST] = host
            unique_id = f"{user_input[CONF_SCHEME]}://{host.lower()}:{user_input[CONF_PORT]}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            client = AqualinkDApiClient(
                async_get_clientsession(
                    self.hass,
                    verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                ),
                host,
                user_input[CONF_PORT],
                user_input[CONF_SCHEME],
                verify_ssl=user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )
            try:
                status = await client.get_status()
                await client.get_devices()
            except AqualinkDApiError:
                errors["base"] = "cannot_connect"
            else:
                title = status.get("panel_type", f"AqualinkD {host}")
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AqualinkDOptionsFlow:
        """Return the options flow."""
        return AqualinkDOptionsFlow(config_entry)


class AqualinkDOptionsFlow(config_entries.OptionsFlow):
    """Manage polling and control options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Show integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self._entry.data, **self._entry.options}
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=current.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL),
                ),
                vol.Optional(
                    CONF_ENABLE_CONTROLS,
                    default=current.get(CONF_ENABLE_CONTROLS, DEFAULT_ENABLE_CONTROLS),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
