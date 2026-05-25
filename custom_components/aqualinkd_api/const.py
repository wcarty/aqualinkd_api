DOMAIN = "aqualinkd_api"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCHEME = "scheme"
CONF_POLL_INTERVAL = "poll_interval"
CONF_VERIFY_SSL = "verify_ssl"
CONF_FILTER_PUMP_ZEROS = "filter_pump_zeros"
CONF_ZERO_GRACE_PERIOD = "zero_grace_period"
CONF_STALE_TIMEOUT = "stale_timeout"
CONF_CREATE_RAW_SENSORS = "create_raw_sensors"

DEFAULT_PORT = 8080
DEFAULT_SCHEME = "http"
DEFAULT_POLL_INTERVAL = 5
DEFAULT_VERIFY_SSL = False
DEFAULT_FILTER_PUMP_ZEROS = True
DEFAULT_ZERO_GRACE_PERIOD = 60
DEFAULT_STALE_TIMEOUT = 300
DEFAULT_CREATE_RAW_SENSORS = False

PLATFORMS = ["sensor", "binary_sensor", "switch", "number", "climate"]
