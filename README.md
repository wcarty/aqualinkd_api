# AqualinkD API

A Python-based Home Assistant integration for the [AqualinkD](https://github.com/aqualinkd/AqualinkD) daemon, providing local HTTP polling and control of Pentair pool equipment.

## 📋 Overview

This project provides a custom Home Assistant integration that communicates directly with the AqualinkD REST API to monitor and control pool equipment including heaters, pumps, lights, and more.

## 🎯 Quick Links

- **Integration Documentation**: See [`custom_components/aqualinkd_api/README.md`](custom_components/aqualinkd_api/README.md) for detailed setup and usage instructions
- **Home Assistant Integration**: Available for custom installation or via HACS
- **License**: GNU General Public License v3.0

## 🚀 Features

- **Local HTTP Polling**: Communicates directly with AqualinkD daemon on your local network
- **Smart Device Discovery**: Automatically scans and merges data from multiple AqualinkD endpoints
- **Climate Control**: Pool and spa heaters as native Home Assistant climate entities
- **Interactive Controls**: Sliders for SWG percentage and VSP RPM adjustments
- **Intelligent Telemetry**: Pump data (RPM, Watts, GPM) with zero-filtering when off
- **Live Configuration**: Adjust polling intervals and timeouts from Home Assistant UI

## 🚀 AI-Powered Development

This project leverages AI to maintain high code quality and security standards. 

- **AI Code Review**: Every Pull Request is reviewed by GPT-4o for logic, performance, and security.
- **Automated Security**: Integrated CodeQL scanning and AI-driven vulnerability detection.
- **Auto-Updates**: Dependabot keeps dependencies updated and secure.

For more details on our development practices, see [DEVELOPMENT.md](DEVELOPMENT.md).

## 📁 Repository Structure

```
aqualinkd_api/
├── custom_components/
│   └── aqualinkd_api/          # Home Assistant integration
│       ├── manifest.json        # Integration metadata
│       ├── const.py            # Configuration constants
│       ├── __init__.py         # Integration initialization
│       └── README.md           # Integration documentation
├── README.md                   # This file
└── LICENSE                     # GPLv3 license
```

## 🔧 Configuration Constants

The integration supports the following configuration options (defined in `const.py`):

| Option | Default | Description |
|--------|---------|-------------|
| `host` | - | IP address or hostname of AqualinkD server |
| `port` | `8080` | Port number for AqualinkD API |
| `scheme` | `http` | HTTP scheme (`http` or `https`) |
| `poll_interval` | `5` | Polling interval in seconds (minimum 2 seconds) |
| `verify_ssl` | `False` | Enable SSL certificate verification |
| `filter_pump_zeros` | `True` | Filter pump telemetry zeros |
| `zero_grace_period` | `60` | Grace period in seconds for pump zero-filtering |
| `stale_timeout` | `300` | Data stale timeout in seconds |
| `create_raw_sensors` | `False` | Create raw sensor entities for debugging |

## 📦 Supported Platforms

- `sensor` - Read-only telemetry and state sensors
- `binary_sensor` - Binary state sensors
- `switch` - Controllable relay switches
- `number` - Numeric setpoint controls
- `climate` - Climate entities for heaters

## 🛠️ Installation

### For Users

See the [Integration README](custom_components/aqualinkd_api/README.md) for complete installation and setup instructions.

### For Developers

1. Clone this repository
2. Copy `custom_components/aqualinkd_api` to your Home Assistant `custom_components` folder
3. Restart Home Assistant
4. Add the integration via **Settings > Devices & Services**

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns in the integration
- Documentation is updated accordingly
- Changes are tested with actual AqualinkD hardware when possible

## 📞 Support

For issues, feature requests, or questions:
1. Check the [Integration README](custom_components/aqualinkd_api/README.md) FAQ section
2. Review existing GitHub issues
3. Create a new issue with detailed information about your setup
