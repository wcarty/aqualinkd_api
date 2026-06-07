"""Stub for homeassistant.config_entries used in tests."""

class ConfigEntry:
    def __init__(self, *args, **kwargs):
        self.entry_id = kwargs.get("entry_id", "test_entry")
