"""Pytest conftest to make `custom_components` importable in CI.

This adds the nearest ancestor directory containing `custom_components`
to `sys.path` so tests can `import custom_components.aqualinkd_api...`.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_custom_components_on_path() -> None:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "custom_components").is_dir():
            sys.path.insert(0, str(parent))
            return


_ensure_custom_components_on_path()


# Provide minimal 'homeassistant' stubs so tests can import package code
def _inject_homeassistant_stub() -> None:
    import types
    import sys

    if "homeassistant" in sys.modules:
        return

    ha = types.ModuleType("homeassistant")
    cfg = types.ModuleType("homeassistant.config_entries")

    class ConfigEntry:  # minimal placeholder used by our package imports
        def __init__(self, *args, **kwargs):
            pass

    cfg.ConfigEntry = ConfigEntry
    ha.config_entries = cfg

    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.config_entries"] = cfg
    # Add other minimal submodules commonly imported by the integration
    const_mod = types.ModuleType("homeassistant.const")
    # Platform used as a simple wrapper around string values in our tests
    class Platform(str):
        pass

    const_mod.Platform = Platform
    sys.modules["homeassistant.const"] = const_mod

    core_mod = types.ModuleType("homeassistant.core")
    class HomeAssistant:  # minimal placeholder for typing
        pass

    core_mod.HomeAssistant = HomeAssistant
    sys.modules["homeassistant.core"] = core_mod

    helpers_mod = types.ModuleType("homeassistant.helpers.aiohttp_client")

    async def async_get_clientsession(hass, verify_ssl: bool = True):
        return None

    helpers_mod.async_get_clientsession = async_get_clientsession
    sys.modules["homeassistant.helpers.aiohttp_client"] = helpers_mod

    # Minimal update_coordinator stub
    upd_mod = types.ModuleType("homeassistant.helpers.update_coordinator")

    class UpdateFailed(Exception):
        pass

    class DataUpdateCoordinator:
        def __class_getitem__(cls, item):
            return cls

        def __init__(self, hass, logger, *, name=None, update_interval=None):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval

        async def async_config_entry_first_refresh(self):
            return None

    upd_mod.UpdateFailed = UpdateFailed
    upd_mod.DataUpdateCoordinator = DataUpdateCoordinator
    sys.modules["homeassistant.helpers.update_coordinator"] = upd_mod

    # Minimal aiohttp stub for API client imports
    aiohttp_mod = types.ModuleType("aiohttp")

    class ClientTimeout:
        def __init__(self, total: int | None = None):
            self.total = total

    class ClientError(Exception):
        pass

    class ClientSession:
        def __init__(self, *args, **kwargs):
            pass

        async def request(self, *args, **kwargs):
            # Simple async context manager stub
            class Resp:
                status = 200

                async def text(self):
                    return "{}"

                async def json(self, content_type=None):
                    return {}

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    return False

            return Resp()

    aiohttp_mod.ClientTimeout = ClientTimeout
    aiohttp_mod.ClientError = ClientError
    aiohttp_mod.ClientSession = ClientSession
    sys.modules["aiohttp"] = aiohttp_mod


_inject_homeassistant_stub()
