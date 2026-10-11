"""Data coordinator for AqualinkD."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AqualinkDApiClient, AqualinkDApiError
from .util import normalize_devices

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AqualinkDData:
    """Normalized data returned by one coordinator refresh."""

    devices: dict[str, dict[str, Any]]
    status: dict[str, Any]


class AqualinkDDataUpdateCoordinator(DataUpdateCoordinator[AqualinkDData]):
    """Poll AqualinkD once and share the result with all entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AqualinkDApiClient,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="AqualinkD API",
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> AqualinkDData:
        try:
            devices_payload = await self.client.get_devices()
            status = await self.client.get_status()
        except AqualinkDApiError as err:
            raise UpdateFailed(str(err)) from err

        devices = normalize_devices(devices_payload)

        if not devices:
            raise UpdateFailed("AqualinkD returned no valid devices")

        return AqualinkDData(devices=devices, status=status)
