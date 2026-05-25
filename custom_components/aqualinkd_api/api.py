from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import quote

import aiohttp

_LOGGER = logging.getLogger(__name__)

class AqualinkDApiError(Exception):
    """Base AqualinkD API error."""

class AqualinkDApiClient:
    def __init__(self, session: aiohttp.ClientSession, host: str, port: int, scheme: str = "http", timeout: int = 10, verify_ssl: bool = False) -> None:
        self._session = session
        self.host = host
        self.port = port
        self.scheme = scheme
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.verify_ssl = verify_ssl

    @property
    def base_url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        _LOGGER.debug("Requesting %s %s", method, url)
        try:
            async with self._session.request(method, url, timeout=self.timeout, ssl=self.verify_ssl if self.scheme == "https" else None, **kwargs) as resp:
                text = await resp.text()
                _LOGGER.debug("Response from %s: HTTP %s: %s", url, resp.status, text[:500])
                if resp.status >= 400:
                    raise AqualinkDApiError(f"{method} {url} returned HTTP {resp.status}: {text[:300]}")
                if method == "GET":
                    try:
                        return await resp.json(content_type=None)
                    except Exception as exc:
                        raise AqualinkDApiError(f"Invalid JSON from {url}: {exc}") from exc
                return text
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            raise AqualinkDApiError(f"Error calling {url}: {exc}") from exc

    async def _request_json(self, path: str) -> dict[str, Any] | list[Any]:
        data = await self._request("GET", path)
        if not isinstance(data, (dict, list)):
            raise AqualinkDApiError(f"{path} did not return a JSON object or list")
        return data

    async def get_devices(self) -> dict[str, Any] | list[Any]:
        return await self._request_json("/api/devices")

    async def get_status(self) -> dict[str, Any] | list[Any]:
        return await self._request_json("/api/status")

    async def get_status_json(self) -> dict[str, Any] | list[Any]:
        return await self._request_json("/status.json")

    async def get_config_json(self) -> dict[str, Any] | list[Any]:
        return await self._request_json("/config.json")

    async def get_schedules(self) -> dict[str, Any] | list[Any]:
        return await self._request_json("/api/schedules")

    async def set_device(self, device_id: str, state: int) -> None:
        """Set a device state (1 for on, 0 for off) using API v2.0."""
        # PUT /api/Filter_Pump/set with value=1
        dev = quote(device_id, safe="")
        # API v2.0 accepts form-post value=1
        await self._request("PUT", f"/api/{dev}/set", data={"value": state})

    async def set_attribute(self, device_id: str, attribute: str, value: str | int | float) -> None:
        """Set an attribute value (like temperature) using API v2.0."""
        # PUT /api/Pool_Heater/setpoint/set with value=85
        dev = quote(device_id, safe="")
        attr = quote(attribute, safe="")
        # API v2.0 accepts form-post value=X
        await self._request("PUT", f"/api/{dev}/{attr}/set", data={"value": value})
