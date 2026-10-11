import asyncio

from custom_components.aqualinkd_api.api import AqualinkDApiClient


class RecordingClient(AqualinkDApiClient):
    def __init__(self):
        super().__init__(session=None, host="aqualinkd.local", port=80)
        self.requests = []

    async def _request(self, method, path, **kwargs):
        self.requests.append((method, path, kwargs))
        return {}


def test_control_paths_preserve_aqualinkd_device_hierarchy():
    client = RecordingClient()

    asyncio.run(client.set_device("SWG/Boost", True))
    asyncio.run(client.set_attribute("Pool_Heater", "setpoint", 86))

    assert client.requests == [
        ("PUT", "/api/SWG/Boost/set", {"data": {"value": 1}}),
        (
            "PUT",
            "/api/Pool_Heater/setpoint/set",
            {"data": {"value": 86}},
        ),
    ]
