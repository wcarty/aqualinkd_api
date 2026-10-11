"""Constants for the AqualinkD API integration."""

from homeassistant.const import Platform

DOMAIN = "aqualinkd_api"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCHEME = "scheme"
CONF_POLL_INTERVAL = "poll_interval"
CONF_VERIFY_SSL = "verify_ssl"
CONF_ENABLE_CONTROLS = "enable_controls"

DEFAULT_PORT = 80
DEFAULT_SCHEME = "http"
DEFAULT_POLL_INTERVAL = 10
DEFAULT_VERIFY_SSL = False
DEFAULT_ENABLE_CONTROLS = False

MIN_POLL_INTERVAL = 5
MAX_POLL_INTERVAL = 300

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]
