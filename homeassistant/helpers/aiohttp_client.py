"""Stub for homeassistant.helpers.aiohttp_client."""

def async_get_clientsession(hass, verify_ssl: bool = True):
    """Return a minimal 'session' object placeholder."""
    class _Session:
        def __init__(self):
            self.verify_ssl = verify_ssl

        def __repr__(self):
            return f"<StubSession verify_ssl={self.verify_ssl}>"

    return _Session()
