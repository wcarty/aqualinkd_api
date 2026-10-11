"""HTTP client for AqualinkD."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

import aiohttp

from .const import DEFAULT_SCHEME, DEFAULT_VERIFY_SSL


class AqualinkDApiError(Exception):
    """Base AqualinkD API error."""


class AqualinkDApiClient:
    """Small async client for the local AqualinkD HTTP API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        scheme: str = DEFAULT_SCHEME,
        *,
        verify_ssl: bool = DEFAULT_VERIFY_SSL,
        timeout: int = 10,
    ) -> None:
        self._session = session
        self.host = host
        self.port = port
        self.scheme = scheme
        self.verify_ssl = verify_ssl
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def base_url(self) -> str:
        """Return the configured controller URL."""
        return f"{self.scheme}://{self.host}:{self.port}"

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                timeout=self._timeout,
                ssl=self.verify_ssl if self.scheme == "https" else None,
                **kwargs,
            ) as response:
                body = await response.text()
                if response.status >= 400:
                    raise AqualinkDApiError(f"{method} {path} returned HTTP {response.status}: {body[:200]}")
                if method == "GET":
                    try:
                        return await response.json(content_type=None)
                    except (ValueError, TypeError) as err:
                        raise AqualinkDApiError(f"{path} returned invalid JSON") from err
                return body
        except (aiohttp.ClientError, TimeoutError) as err:
            raise AqualinkDApiError(f"Request to {path} failed: {err}") from err

    async def get_devices(self) -> dict[str, Any]:
        """Fetch and validate the equipment payload."""
        data = await self._request("GET", "/api/devices")
        if not isinstance(data, dict) or not isinstance(data.get("devices"), list):
            raise AqualinkDApiError("/api/devices returned an unexpected payload")
        return data

    async def get_status(self) -> dict[str, Any]:
        """Fetch and validate controller status."""
        data = await self._request("GET", "/api/status")
        if not isinstance(data, dict):
            raise AqualinkDApiError("/api/status returned an unexpected payload")
        return data

    async def set_device(self, device_id: str, state: bool) -> None:
        """Turn an AqualinkD equipment item on or off."""
        path_id = quote(device_id, safe="/")
        await self._request("PUT", f"/api/{path_id}/set", data={"value": 1 if state else 0})

    async def set_attribute(self, device_id: str, attribute: str, value: str | int | float) -> None:
        """Set an AqualinkD equipment attribute."""
        path_id = quote(device_id, safe="/")
        path_attribute = quote(attribute, safe="")
        await self._request(
            "PUT",
            f"/api/{path_id}/{path_attribute}/set",
            data={"value": value},
        )
