from custom_components.aqualinkd_api.util import flatten_devices, slugify


def test_slugify_basic():
    assert slugify("Pool Heater") == "pool_heater"
    assert slugify("/Path/To/Value") == "path_to_value"


def test_flatten_devices_with_containers():
    data = {
        "leds": {"Aux_3": "off"},
        "devices": [{"type": "switch", "id": "Aux_3", "name": "Spill Over", "state": "off"}],
    }
    flat = flatten_devices(data)
    # should contain an entry for the named device and the container item
    assert any(isinstance(k, str) for k in flat.keys())
    assert any(d.get("id") == "Aux_3" for d in flat.values())
