from custom_components.aqualinkd_api.util import (
    as_bool,
    as_float,
    normalize_devices,
)


def test_value_conversions():
    assert as_bool("enabled") is True
    assert as_bool("off") is False
    assert as_bool("unknown") is None
    assert as_float("7.5") == 7.5
    assert as_float("-999") == -999
    assert as_float("unknown") is None


def test_normalize_devices_uses_stable_ids():
    payload = {
        "devices": [
            {
                "type": "switch",
                "id": "Aux_1",
                "name": "Pool Light",
                "state": "off",
            },
            {
                "type": "value",
                "id": "CHEM/pH",
                "name": "Water Chemistry pH",
                "value": "7.5",
            },
            {"name": "Missing ID"},
            "invalid",
        ]
    }

    devices = normalize_devices(payload)

    assert set(devices) == {"Aux_1", "CHEM/pH"}
    assert devices["CHEM/pH"]["value"] == "7.5"
