"""Value conversion helpers for AqualinkD."""

from __future__ import annotations

from typing import Any


def as_bool(value: Any) -> bool | None:
    """Convert common AqualinkD state values to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()
    if normalized in {"on", "true", "1", "enabled", "yes"}:
        return True
    if normalized in {"off", "false", "0", "disabled", "no"}:
        return False
    return None


def as_float(value: Any) -> float | None:
    """Convert an AqualinkD numeric value to float."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_devices(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index valid /api/devices entries by stable AqualinkD ID."""
    devices: dict[str, dict[str, Any]] = {}
    raw_devices = payload.get("devices")
    if not isinstance(raw_devices, list):
        return devices

    for raw_device in raw_devices:
        if not isinstance(raw_device, dict):
            continue
        device_id = raw_device.get("id")
        if isinstance(device_id, str) and device_id:
            devices[device_id] = raw_device
    return devices


def pump_status_records(status: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index per-pump /api/status records by stable equipment ID."""
    pumps: dict[str, dict[str, Any]] = {}
    for key, value in status.items():
        if not key.startswith("Pump_") or not isinstance(value, dict):
            continue
        device_id = value.get("id")
        if isinstance(device_id, str) and device_id:
            pumps[device_id] = value
    return pumps
