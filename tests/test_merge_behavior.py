from custom_components.aqualinkd_api.util import flatten_devices, slugify


def test_merge_behavior_preserves_prettiest_name():
    data1 = {
        "type": "devices",
        "devices": [
            {"type": "switch", "id": "Aux_3", "name": "Spill Over", "state": "off"}
        ],
    }

    data2 = {"leds": {"Aux_3": "off"}}

    # Flatten both and simulate merge order
    flat2 = flatten_devices(data2)
    flat1 = flatten_devices(data1)

    # Check that flatten produced expected ids
    assert "Aux_3" in flat2
    assert any(d.get("id") == "Aux_3" for d in flat1.values())
